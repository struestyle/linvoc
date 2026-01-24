"""Factory et abstraction pour l'injection de texte."""

from abc import ABC, abstractmethod
from typing import Optional

from .environment import EnvironmentDetector, SessionType


class TextInjectorBackend(ABC):
    """Interface abstraite pour les backends d'injection de texte."""

    @abstractmethod
    def inject_text(self, text: str) -> bool:
        """
        Injecte du texte dans l'application active.
        
        Args:
            text: Texte à injecter
            
        Returns:
            bool: True si l'injection a réussi
        """
        pass

    @abstractmethod
    def is_available(self) -> bool:
        """
        Vérifie si ce backend est disponible.
        
        Returns:
            bool: True si le backend peut être utilisé
        """
        pass

    @property
    @abstractmethod
    def name(self) -> str:
        """Nom du backend."""
        pass


class TextInjector:
    """
    Factory pour créer le backend d'injection approprié.
    
    Sélectionne automatiquement le meilleur backend selon l'environnement.
    """

    _instance: Optional[TextInjectorBackend] = None

    @classmethod
    def create(cls, force_backend: Optional[str] = None) -> TextInjectorBackend:
        """
        Crée le backend d'injection approprié.
        
        Args:
            force_backend: Forcer un backend spécifique ('xdotool', 'portal', 'ydotool')
            
        Returns:
            TextInjectorBackend: Backend configuré
            
        Raises:
            RuntimeError: Si aucun backend n'est disponible
        """
        # Import lazy pour éviter les imports circulaires
        from ..backends.xdotool_backend import XdotoolBackend
        from ..backends.portal_backend import PortalBackend
        from ..backends.ydotool_backend import YdotoolBackend

        # Si un backend est forcé
        if force_backend:
            backends = {
                "xdotool": XdotoolBackend,
                "portal": PortalBackend,
                "ydotool": YdotoolBackend,
            }
            if force_backend in backends:
                backend = backends[force_backend]()
                if backend.is_available():
                    cls._instance = backend
                    return backend
                raise RuntimeError(f"Backend '{force_backend}' non disponible")
            raise ValueError(f"Backend inconnu: {force_backend}")

        # Sélection automatique basée sur l'environnement
        recommended = EnvironmentDetector.get_recommended_backend()
        
        # Ordre de priorité selon la recommandation
        if recommended == "portal":
            priority = [PortalBackend, XdotoolBackend, YdotoolBackend]
        elif recommended == "xdotool":
            priority = [XdotoolBackend, PortalBackend, YdotoolBackend]
        elif recommended == "ydotool":
            priority = [YdotoolBackend, PortalBackend, XdotoolBackend]
        else:
            priority = [XdotoolBackend, PortalBackend, YdotoolBackend]

        # Essayer chaque backend dans l'ordre
        for BackendClass in priority:
            try:
                backend = BackendClass()
                if backend.is_available():
                    cls._instance = backend
                    return backend
            except Exception:
                continue

        raise RuntimeError(
            "Aucun backend d'injection de texte disponible. "
            "Installez xdotool (X11) ou ydotool (Wayland)."
        )

    @classmethod
    def get_instance(cls) -> TextInjectorBackend:
        """
        Retourne l'instance actuelle ou en crée une nouvelle.
        
        Returns:
            TextInjectorBackend: Backend configuré
        """
        if cls._instance is None:
            cls._instance = cls.create()
        return cls._instance

    @classmethod
    def inject(cls, text: str) -> bool:
        """
        Raccourci pour injecter du texte.
        
        Args:
            text: Texte à injecter
            
        Returns:
            bool: True si succès
        """
        return cls.get_instance().inject_text(text)
