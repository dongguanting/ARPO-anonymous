from abc import ABC, abstractmethod


class BaseTool(ABC):
    """Abstract base class that defines common interface for all tools"""
    
    @property
    @abstractmethod
    def name(self) -> str:
        """Tool name"""
        pass
    
    @property
    @abstractmethod
    def trigger_tag(self) -> str:
        """Tag used to trigger this tool"""
        pass
    
    @abstractmethod
    def execute(self, content: str, **kwargs) -> str:
        """Execute tool operation"""
        pass