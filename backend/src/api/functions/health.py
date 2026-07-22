async def health_check():
    return {
        "status": "healthy",
        "service": "Blog Writing Agenti API",
    }