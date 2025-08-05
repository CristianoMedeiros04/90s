"""
Módulo de Autenticação
Sistema de login simples para o Gerador de Roteiros
"""

from .login import check_authentication, logout, render_logout_button

__all__ = ['check_authentication', 'logout', 'render_logout_button']

