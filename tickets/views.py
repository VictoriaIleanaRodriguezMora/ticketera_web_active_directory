import csv
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.http import HttpResponse
from django.db import transaction
from django.db.models import Q
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
    prioridad = request.GET.get('prioridad', '')
    busqueda = request.GET.get('q', '').strip()[:150]
    if estado in Ticket.Estado.values:
        qs = qs.filter(estado=estado)
    if prioridad in Ticket.Prioridad.values:
        qs = qs.filter(prioridad=prioridad)
    if busqueda:
        qs = qs.filter(Q(titulo__icontains=busqueda) | Q(descripcion__icontains=busqueda))
    return render(request, 'tickets/list.html', {
        'tickets': qs, 'estado': estado, 'estados': Ticket.Estado.choices,
        'prioridad': prioridad, 'prioridades': Ticket.Prioridad.choices,
        'busqueda': busqueda, 'rol': rol(request.user),
    })

@login_required
@require_http_methods(['GET', 'POST'])
def ticket_create(request):
    exigir_rol(request.user, 'Admin', 'Operador', 'Usuario')
    form = TicketCreateForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        ticket = form.save(commit=False)
        ticket.creado_por = request.user
        with transaction.atomic():
            ticket.save()
            ticket.seguimientos.create(autor=request.user, texto='Ticket creado.')
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
        # Comparar con una nueva consulta a BD: ModelForm.is_valid() ya
        # puede haber actualizado los atributos de la instancia en memoria.
        anterior = Ticket.objects.get(pk=ticket.pk)
        cambios = []
        if anterior.estado != ticket.estado:
            cambios.append(f"Estado: {anterior.get_estado_display()} -> {ticket.get_estado_display()}")
        if anterior.prioridad != ticket.prioridad:
            cambios.append(f"Prioridad: {anterior.get_prioridad_display()} -> {ticket.get_prioridad_display()}")
        if anterior.responsable_id != ticket.responsable_id:
            antes = anterior.responsable.username if anterior.responsable else 'Sin asignar'
            despues = ticket.responsable.username if ticket.responsable else 'Sin asignar'
            cambios.append(f"Responsable: {antes} -> {despues}")
        if anterior.titulo != ticket.titulo:
            cambios.append('Título actualizado')
        if anterior.descripcion != ticket.descripcion:
            cambios.append('Descripción actualizada')
        with transaction.atomic():
            ticket = form.save()
            if cambios:
                ticket.seguimientos.create(autor=request.user, texto='; '.join(cambios))
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
