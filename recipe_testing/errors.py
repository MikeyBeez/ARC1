"""Error classes for recipe testing"""

class RecipeTestError(Exception):
    """Base class for recipe testing errors"""
    pass

class TaskError(RecipeTestError):
    """Error in task data structure or validation"""
    pass

class ExecutionError(RecipeTestError):
    """Error during recipe execution"""
    pass

class SerializationError(RecipeTestError):
    """Error during data serialization"""
    pass