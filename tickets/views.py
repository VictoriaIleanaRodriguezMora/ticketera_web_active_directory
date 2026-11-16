import csv
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.views.decorators.http import require_http_methods
from .forms import TicketCreateForm, TicketEditForm, SeguimientoForm
from .models import Ticket
from .permissions import rol, puede_ver, exigir_rol


def tickets_visibles(usuario):
    r = rol(usuario)
    if r == 'Usuario':
        return Ticket.objects.filter(creado_por=usuario)
    if r in ('Admin', 'Operador', 'Consulta'):
        return Ticket.objects.all()
    raise PermissionDenied('Tu cuenta no tiene un rol asignado.')

@login_required
@require_http_methods(['GET'])
def ticket_list(request):
    qs = tickets_visibles(request.user).select_related('creado_por', 'responsable')
    estado = request.GET.get('estado', '')
    if estado in Ticket.Estado.values:
        qs = qs.filter(estado=estado)
    return render(request, 'tickets/list.html', {'tickets': qs, 'estado': estado, 'estados': Ticket.Estado.choices, 'rol': rol(request.user)})

@login_required
@require_http_methods(['GET', 'POST'])
def ticket_create(request):
    exigir_rol(request.user, 'Admin', 'Operador', 'Usuario')
    form = TicketCreateForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        ticket = form.save(commit=False)
        ticket.creado_por = request.user
        ticket.save()
        return redirect('ticket_detail', pk=ticket.pk)
    return render(request, 'tickets/form.html', {'form': form, 'titulo': 'Nuevo ticket'})

@login_required
@require_http_methods(['GET'])
def ticket_detail(request, pk):
    ticket = get_object_or_404(Ticket.objects.select_related('creado_por', 'responsable'), pk=pk)
    if not puede_ver(request.user, ticket):
        raise PermissionDenied
    puede_comentar = rol(request.user) in ('Admin', 'Operador') or (rol(request.user) == 'Usuario' and ticket.creado_por_id == request.user.pk)
    return render(request, 'tickets/detail.html', {'ticket': ticket, 'seguimientos': ticket.seguimientos.select_related('autor'), 'form': SeguimientoForm(), 'puede_editar': rol(request.user) in ('Admin', 'Operador'), 'puede_comentar': puede_comentar})

@login_required
@require_http_methods(['GET', 'POST'])
def ticket_edit(request, pk):
    exigir_rol(request.user, 'Admin', 'Operador')
    ticket = get_object_or_404(Ticket, pk=pk)
    form = TicketEditForm(request.POST or None, instance=ticket)
    if request.method == 'POST' and form.is_valid():
        anterior = (ticket.estado, ticket.prioridad, ticket.responsable_id)
        ticket = form.save()
        cambios = []
        if anterior[0] != ticket.estado: cambios.append('Estado actualizado')
        if anterior[1] != ticket.prioridad: cambios.append('Prioridad actualizada')
        if anterior[2] != ticket.responsable_id: cambios.append('Responsable actualizado')
        if cambios:
            ticket.seguimientos.create(autor=request.user, texto=' / '.join(cambios))
        return redirect('ticket_detail', pk=ticket.pk)
    return render(request, 'tickets/form.html', {'form': form, 'titulo': f'Editar ticket #{ticket.pk}'})

@login_required
@require_http_methods(['POST'])
def ticket_comment(request, pk):
    ticket = get_object_or_404(Ticket, pk=pk)
    if not puede_ver(request.user, ticket) or rol(request.user) == 'Consulta':
        raise PermissionDenied
    form = SeguimientoForm(request.POST)
    if form.is_valid():
        seguimiento = form.save(commit=False)
        seguimiento.ticket = ticket
        seguimiento.autor = request.user
        seguimiento.save()
    return redirect('ticket_detail', pk=ticket.pk)

@login_required
@require_http_methods(['GET'])
def ticket_export(request):
    exigir_rol(request.user, 'Admin', 'Operador')
    response = HttpResponse(content_type='text/csv; charset=utf-8')
    response['Content-Disposition'] = 'attachment; filename="tickets.csv"'
    response.write('\ufeff')
    writer = csv.writer(response)
    writer.writerow(['ID', 'Título', 'Estado', 'Prioridad', 'Creado por', 'Responsable', 'Creado el'])
    for t in tickets_visibles(request.user).select_related('creado_por', 'responsable'):
        writer.writerow([t.pk, t.titulo, t.get_estado_display(), t.get_prioridad_display(), t.creado_por.username, t.responsable.username if t.responsable else '', timezone.localtime(t.creado_el).strftime('%Y-%m-%d %H:%M')])
    return response
