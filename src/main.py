#!/usr/bin/env python3
"""
linvoc - Application de dictée vocale pour Linux.

Point d'entrée principal de l'application.
"""

import sys
import argparse

from .core.environment import EnvironmentDetector
# from .gui.main_window import LinvocApplication  # Importé localement pour éviter les hangs en mode CLI


def print_environment_info():
    """Affiche les informations d'environnement."""
    info = EnvironmentDetector.get_environment_info()

    print("=== Environnement linvoc ===")
    print(f"Session: {info['session_type']}")
    print(f"Bureau: {info['desktop_environment']}")
    print(f"XDG Portal: {'✓' if info['has_portal'] else '✗'}")
    print(f"xdotool: {'✓' if info['has_xdotool'] else '✗'}")
    print(f"ydotool: {'✓' if info['has_ydotool'] else '✗'}")
    print(f"nerd-dictation (VOSK): {'✓' if info['has_nerd_dictation'] else '✗'}")
    print(f"pywhispercpp (Whisper): {'✓' if info['has_whisper'] else '✗'}")
    print(f"faster-whisper: {'✓' if info['has_faster_whisper'] else '✗'}")
    print(f"nemo_toolkit (Parakeet): {'✓' if info['has_parakeet'] else '✗'}")
    print(f"Backend recommandé: {info['recommended_backend']}")
    print("============================")


def check_dependencies(engine: str = "vosk") -> bool:
    """
    Vérifie que les dépendances sont disponibles.

    Args:
        engine: Moteur à vérifier ('vosk' ou 'whisper')

    Returns:
        bool: True si tout est OK
    """
    info = EnvironmentDetector.get_environment_info()

    errors = []

    # Vérifier le moteur de reconnaissance
    if engine == "whisper":
        if not info['has_whisper']:
            errors.append(
                "pywhispercpp n'est pas installé.\n"
                "Installation: pip install pywhispercpp PyAudio\n"
                "Ou réinstallez linvoc: pip install -e ."
            )
    elif engine == "parakeet":
        if not info["has_parakeet"]:
            errors.append(
                "nemo_toolkit (Parakeet) n'est pas installé.\n"
                "Installation (GPU recommandé): pip install 'linvoc[parakeet]'\n"
                "Assurez-vous que PyTorch compatible CUDA est présent."
            )
    elif engine == "faster-whisper":
        if not info['has_faster_whisper']:
            errors.append(
                "faster-whisper n'est pas installé.\n"
                "Installation: pip install 'linvoc[fasterwhisper]'\n"
                "Ou: pip install faster-whisper"
            )
    elif engine == "faster-whisper":
        if not info['has_faster_whisper']:
            errors.append(
                "faster-whisper n'est pas installé.\n"
                "Installation: pip install 'linvoc[fasterwhisper]'\n"
                "Ou: pip install faster-whisper"
            )
    else:
        if not info['has_nerd_dictation']:
            errors.append(
                "nerd-dictation n'est pas installé.\n"
                "Installation: pip install "
                "\"git+https://github.com/ideasman42/nerd-dictation.git"
                "#subdirectory=package/python\"\n"
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
  linvoc                    Lancer l'application (moteur VOSK)
  linvoc --engine whisper   Utiliser Whisper comme moteur
  linvoc --engine parakeet  Utiliser Parakeet (NVIDIA NeMo)
  linvoc --daemon --engine parakeet  Démarrer Parakeet en tâche de fond
  linvoc --toggle            Basculer une instance déjà ouverte
  linvoc --info             Afficher les infos d'environnement
  linvoc --check            Vérifier les dépendances
  linvoc --lang en          Utiliser l'anglais
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
        "--engine", "-e",
        choices=["vosk", "whisper", "faster-whisper", "parakeet"],
        default="vosk",
        help="Moteur de reconnaissance vocale (défaut: vosk)"
    )

    parser.add_argument(
        "--model-size", "-m",
        choices=["tiny", "base", "small", "medium", "large"],
        default="base",
        help="Taille du modèle Whisper (défaut: base)"
    )

    parser.add_argument(
        "--parakeet-model",
        default="nvidia/parakeet-tdt-0.6b-v3",
        help="Nom du modèle pré-entraîné Parakeet (défaut: nvidia/parakeet-tdt-0.6b-v3)"
    )

    parser.add_argument(
        "--daemon",
        action="store_true",
        help="Démarrer linvoc en mode service persistant (ne se ferme pas dès qu'une instance existe)"
    )

    parser.add_argument(
        "--toggle",
        action="store_true",
        help="Basculer enregistrement/arrêt sur l'instance déjà en cours"
    )

    parser.add_argument(
        "--daemon-ui",
        action="store_true",
        help="Afficher l'UI en mode daemon (sinon cachée)"
    )

    parser.add_argument(
        "--force-preload",
        action="store_true",
        help="Charge le moteur immédiatement au lancement (utile pour daemon)"
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

    from .core.single_instance import get_running_pid, send_toggle_signal

    DEFAULT_SCOPE = "linvoc"
    DAEMON_SCOPE = "linvoc-daemon"
    lock_scope = DAEMON_SCOPE if args.daemon else DEFAULT_SCOPE
    show_window = True
    auto_hide = False
    preload_only = False

    if args.daemon and not args.daemon_ui:
        show_window = False
        auto_hide = True
        if not args.start and args.force_preload:
            preload_only = True

    if args.toggle:
        existing_pid = get_running_pid(scope=DAEMON_SCOPE)
        if not existing_pid:
            print("Aucune instance linvoc n'est en cours d'exécution.")
            return 1
        if send_toggle_signal(existing_pid):
            return 0
        print("Impossible d'envoyer le signal au processus existant.")
        return 1

    # Mode info
    if args.info:
        print_environment_info()
        return 0

    # Mode vérification
    if args.check:
        print_environment_info()
        print()
        if check_dependencies(args.engine):
            print("✓ Toutes les dépendances sont satisfaites.")
            return 0
        return 1

    # Vérification rapide des dépendances
    if not check_dependencies(args.engine):
        print("\nUtilisez --check pour plus de détails.")
        return 1

    # Vérifier si une instance est déjà en cours
    existing_pid = get_running_pid(scope=lock_scope)

    if existing_pid:
        if args.daemon:
            print("Une instance linvoc tourne déjà (PID {}).".format(existing_pid))
            print("Utilisez --toggle pour démarrer/arrêter l'écoute.")
            return 0
        # Instance existante : envoyer le signal toggle
        if send_toggle_signal(existing_pid):
            return 0
        # Si échec, continuer et lancer une nouvelle instance

    # Lancer l'application avec le moteur choisi
    from .gui.main_window import LinvocApplication
    app = LinvocApplication(
        start_immediately=args.start,
        preload_only=preload_only,
        engine_type=args.engine,
        language=args.lang,
        model_size=args.model_size,
        parakeet_model=args.parakeet_model,
        lock_scope=lock_scope,
        show_window=show_window,
        auto_hide=auto_hide,
    )
    return app.run()


if __name__ == "__main__":
    sys.exit(main())
