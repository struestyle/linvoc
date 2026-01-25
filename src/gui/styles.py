"""Styles et thèmes pour l'interface graphique."""

from typing import Dict


class Styles:
    """Gestion des styles QSS pour l'application."""

    # Couleurs du thème
    COLORS: Dict[str, Dict[str, str]] = {
        "dark": {
            "background": "#1e1e2e",
            "surface": "#313244",
            "primary": "#cba6f7",      # Mauve
            "recording": "#f38ba8",     # Rouge/Rose
            "success": "#a6e3a1",       # Vert
            "warning": "#fab387",       # Orange
            "text": "#cdd6f4",
            "text_muted": "#6c7086",
            "border": "#45475a",
        },
        "light": {
            "background": "#eff1f5",
            "surface": "#dce0e8",
            "primary": "#8839ef",
            "recording": "#d20f39",
            "success": "#40a02b",
            "warning": "#fe640b",
            "text": "#4c4f69",
            "text_muted": "#8c8fa1",
            "border": "#bcc0cc",
        }
    }

    @classmethod
    def get_theme_colors(cls, dark_mode: bool = True) -> Dict[str, str]:
        """
        Retourne les couleurs du thème.

        Args:
            dark_mode: True pour le thème sombre

        Returns:
            dict: Couleurs du thème
        """
        return cls.COLORS["dark" if dark_mode else "light"]

    @classmethod
    def get_widget_style(cls, dark_mode: bool = True) -> str:
        """
        Retourne le QSS pour le widget principal.

        Args:
            dark_mode: True pour le thème sombre

        Returns:
            str: Feuille de style QSS
        """
        colors = cls.get_theme_colors(dark_mode)

        return f"""
            QWidget#MicrophoneWidget {{
                background-color: {colors['surface']};
                border: 2px solid {colors['border']};
                border-radius: 16px;
            }}

            QLabel#StatusLabel {{
                color: {colors['text_muted']};
                font-size: 10px;
                font-weight: 500;
            }}

            QLabel#MicIcon {{
                color: {colors['text']};
            }}
        """

    @classmethod
    def get_recording_style(cls, dark_mode: bool = True) -> str:
        """
        Retourne le QSS pour l'état enregistrement.

        Args:
            dark_mode: True pour le thème sombre

        Returns:
            str: Feuille de style QSS
        """
        colors = cls.get_theme_colors(dark_mode)

        return f"""
            QWidget#MicrophoneWidget {{
                background-color: {colors['surface']};
                border: 2px solid {colors['recording']};
                border-radius: 16px;
            }}

            QLabel#StatusLabel {{
                color: {colors['recording']};
                font-size: 10px;
                font-weight: 600;
            }}

            QLabel#MicIcon {{
                color: {colors['recording']};
            }}
        """

    @classmethod
    def get_processing_style(cls, dark_mode: bool = True) -> str:
        """
        Retourne le QSS pour l'état traitement.

        Args:
            dark_mode: True pour le thème sombre

        Returns:
            str: Feuille de style QSS
        """
        colors = cls.get_theme_colors(dark_mode)

        return f"""
            QWidget#MicrophoneWidget {{
                background-color: {colors['surface']};
                border: 2px solid {colors['primary']};
                border-radius: 16px;
            }}

            QLabel#StatusLabel {{
                color: {colors['primary']};
                font-size: 10px;
                font-weight: 500;
            }}
        """

    @classmethod
    def get_error_style(cls, dark_mode: bool = True) -> str:
        """
        Retourne le QSS pour l'état erreur.

        Args:
            dark_mode: True pour le thème sombre

        Returns:
            str: Feuille de style QSS
        """
        colors = cls.get_theme_colors(dark_mode)

        return f"""
            QWidget#MicrophoneWidget {{
                background-color: {colors['surface']};
                border: 2px solid {colors['warning']};
                border-radius: 16px;
            }}

            QLabel#StatusLabel {{
                color: {colors['warning']};
                font-size: 10px;
                font-weight: 600;
            }}
        """


# Icônes SVG pour les différents états
ICONS = {
    "microphone": """
        <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
            <path d="M12 2C10.3431 2 9 3.34315 9 5V11C9 12.6569 10.3431 14 12 14C13.6569 14 15 12.6569 15 11V5C15 3.34315 13.6569 2 12 2Z" fill="currentColor"/>
            <path d="M19 11C19 14.534 16.398 17.46 13 17.923V21H11V17.923C7.602 17.46 5 14.534 5 11H7C7 13.761 9.239 16 12 16C14.761 16 17 13.761 17 11H19Z" fill="currentColor"/>
        </svg>
    """,
    "microphone_on": """
        <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
            <path d="M12 2C10.3431 2 9 3.34315 9 5V11C9 12.6569 10.3431 14 12 14C13.6569 14 15 12.6569 15 11V5C15 3.34315 13.6569 2 12 2Z" fill="currentColor"/>
            <path d="M19 11C19 14.534 16.398 17.46 13 17.923V21H11V17.923C7.602 17.46 5 14.534 5 11H7C7 13.761 9.239 16 12 16C14.761 16 17 13.761 17 11H19Z" fill="currentColor"/>
            <circle cx="12" cy="11" r="14" stroke="currentColor" stroke-width="0.5" opacity="0.3">
                <animate attributeName="r" from="10" to="16" dur="1.5s" repeatCount="indefinite" />
                <animate attributeName="opacity" from="0.3" to="0" dur="1.5s" repeatCount="indefinite" />
            </circle>
        </svg>
    """,
    "spinner": """
        <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
            <path d="M12 2V4M12 20V22M4 12H2M22 12H20M19.07 4.93L17.66 6.34M6.34 17.66L4.93 19.07M19.07 19.07L17.66 17.66M6.34 6.34L4.93 4.93" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
        </svg>
    """,
    "warning": """
        <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
            <path d="M12 8V12M12 16H12.01M22 12C22 17.5228 17.5228 22 12 22C6.47715 22 2 17.5228 2 12C2 6.47715 6.47715 2 12 2C17.5228 2 22 6.47715 22 12Z" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
        </svg>
    """,
    "close": """
        <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
            <path d="M18 6L6 18M6 6L18 18" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
        </svg>
    """
}
