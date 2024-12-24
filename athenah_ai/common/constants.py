ignore_patterns = [
    "node_modules*",
    "dist*",
    "build*",
    ".git*",
    ".venv*",
    ".vscode*",
    "__pycache__*",
    "poetry.lock",
]

file_config_template: str = """
{
    "name": "Name of the file with extension",
    "description": "Description of the file",
    "classes": [
        {
            "name": "Name of class",
            "description": "Description of the class",
            "methods": [
                {
                    "name": "Name of method (code)",
                    "snippet": "Short snippet of the method",
                    "description": "Description of the method"
                }
            ]
        }
    ],
    "functions": [
        {
            "name": "Name of the function",
            "snippet": "Short snippet of the function",
            "line_number": Line number of the function in the file,
            "description": "Description of the function"
        }
    ]
}
"""

directory_config_template: str = f"""
{
    "name": "Name of the directory",
    "description": "Description of the directory",
    "files": [
        {file_config_template}
    ]
}
"""
