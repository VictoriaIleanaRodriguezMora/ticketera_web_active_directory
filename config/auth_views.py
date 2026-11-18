from datetime import time

from django.contrib.auth.views import LoginView
from django.utils import timezone


class LoginConHorarioView(LoginView):
    template_name = "registration/login.html"

    def form_valid(self, form):
        # El horario se calcula en la zona horaria configurada en Django.
        # Desde las 08:00 inclusive hasta las 18:00 exclusive.
        hora_actual = timezone.localtime().time()
        if not (time(8, 0) <= hora_actual < time(18, 0)):
            form.add_error(None, "El inicio de sesión está permitido únicamente de 08:00 a 18:00 (hora argentina).")
            return self.form_invalid(form)
        return super().form_valid(form)
