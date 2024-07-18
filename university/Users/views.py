from django.conf import settings
from django.contrib.auth import authenticate, login, logout
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views import View
from django.utils.decorators import method_decorator
from .forms import CustomAuthenticationForm, CustomUserCreationForm

User = settings.AUTH_USER_MODEL

@login_required
def index(request):
    """Render the index page for authenticated users."""
    return render(request, "authentication/index.html")

class SignInView(View):
    """Handle user sign in."""
    template_name = "authentication/sign_in.html"
    form_class = CustomAuthenticationForm

    def get(self, request):
        """Render the sign in page."""
        if request.user.is_authenticated:
            return redirect('Users:dashboard')
        return render(request, self.template_name, {'form': self.form_class()})

    def post(self, request):
        """Process the sign in form."""
        form = self.form_class(request.POST)
        if form.is_valid():
            email = form.cleaned_data.get('email')
            password = form.cleaned_data.get('password')
            remember_me = form.cleaned_data.get('remember_me')
            user = authenticate(request, username=email, password=password)
            if user is not None:
                login(request, user)
                if remember_me:
                    request.session.set_expiry(60 * 60 * 24 * 30)  # 30 days
                else:
                    request.session.set_expiry(0)  # Browser session
                return redirect('Users:dashboard')
        return render(request, self.template_name, {'form': form})

# class SignUpView(View):
#     """Handle user sign up."""
#     template_name = "authentication/sign_up.html"
#     form_class = CustomUserCreationForm

#     def get(self, request):
#         """Render the sign up page."""
#         return render(request, self.template_name, {'form': self.form_class()})

#     def post(self, request):
#         """Process the sign up form."""
#         form = self.form_class(request.POST)
#         if form.is_valid():
#             user = form.save()
#             login(request, user)
#             return redirect('Users:dashboard')
#         return render(request, self.template_name, {'form': form})

@login_required
def logout_view(request):
    """Log out the user and redirect to sign in page."""
    logout(request)
    return redirect("Users:sign-in")