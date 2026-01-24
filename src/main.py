#!/usr/bin/env python3
"""
linvoc - Application de dictée vocale pour Linux.

Point d'entrée principal de l'application.
"""

import sys
import argparse

from PySide6.QtWidgets import QApplication

from .core.environment import EnvironmentDetector
from .gui.main_window import MicrophoneWidget, LinvocApplication


def print_environment_info():
    """Affiche les informations d'environnement."""
    info = EnvironmentDetector.get_environment_info()
    
    print("=== Environnement linvoc ===")
    print(f"Session: {info['session_type']}")
    print(f"Bureau: {info['desktop_environment']}")
    print(f"XDG Portal: {'✓' if info['has_portal'] else '✗'}")
    print(f"xdotool: {'✓' if info['has_xdotool'] else '✗'}")
    print(f"ydotool: {'✓' if info['has_ydotool'] else '✗'}")
    print(f"nerd-dictation: {'✓' if info['has_nerd_dictation'] else '✗'}")
    print(f"Backend recommandé: {info['recommended_backend']}")
    print("============================")


def check_dependencies() -> bool:
    """
    Vérifie que les dépendances sont disponibles.
    
    Returns:
        bool: True si tout est OK
    """
    info = EnvironmentDetector.get_environment_info()
    
    errors = []
    
    # Vérifier nerd-dictation
    if not info['has_nerd_dictation']:
        errors.append(
            "nerd-dictation n'est pas installé.\n"
            "Installation: pip install \"git+https://github.com/ideasman42/nerd-dictation.git#subdirectory=package/python\"\n"
            "Modèle: Télécharger et extraire dans ~/.config/nerd-dictation/model"
        )
    
    # Vérifier un backend d'injection
    if info['recommended_backend'] == 'none':
        session = info['session_type']
        if session == 'x11':
            errors.append(
                "Aucun outil d'injection de texte trouvé.\n"
                "Installation X11: sudo apt install xdotool"
            )
        else:
            errors.append(
                "Aucun outil d'injection de texte trouvé.\n"
                "Installation Wayland: sudo apt install wl-clipboard ydotool\n"
                "Puis: sudo systemctl enable --now ydotool"
            )
    
    if errors:
        print("⚠️  Dépendances manquantes:\n")
        for error in errors:
            print(f"  • {error}\n")
        return False
    
    return True


def main():
    """Point d'entrée principal."""
    parser = argparse.ArgumentParser(
        description="linvoc - Dictée vocale pour Linux",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Exemples:
  linvoc              Lancer l'application
  linvoc --info       Afficher les infos d'environnement
  linvoc --check      Vérifier les dépendances
  linvoc --lang en    Utiliser l'anglais
        """
    )
    
    parser.add_argument(
        "--info", "-i",
        action="store_true",
        help="Afficher les informations d'environnement"
    )
    
    parser.add_argument(
        "--check", "-c",
        action="store_true",
        help="Vérifier les dépendances et quitter"
    )
    
    parser.add_argument(
        "--lang", "-l",
        default="fr",
        help="Code langue pour la dictée (défaut: fr)"
    )
    
    parser.add_argument(
        "--backend", "-b",
        choices=["auto", "xdotool", "portal", "ydotool"],
        default="auto",
        help="Backend d'injection de texte (défaut: auto)"
    )
    
    parser.add_argument(
        "--version", "-v",
        action="version",
        version="linvoc 0.1.0"
    )
    
    parser.add_argument(
        "--start", "-s",
        action="store_true",
        help="Démarrer l'enregistrement immédiatement au lancement"
    )
    
    args = parser.parse_args()
    
    # Mode info
    if args.info:
        print_environment_info()
        return 0
    
    # Mode vérification
    if args.check:
        print_environment_info()
        print()
        if check_dependencies():
            print("✓ Toutes les dépendances sont satisfaites.")
            return 0
        return 1
    
    # Vérification rapide des dépendances
    if not check_dependencies():
        print("\nUtilisez --check pour plus de détails.")
        return 1
    
    # Lancer l'application
    app = LinvocApplication(start_immediately=args.start)
    return app.run()


if __name__ == "__main__":
    sys.exit(main())
