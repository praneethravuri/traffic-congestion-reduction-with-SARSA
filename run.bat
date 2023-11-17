@echo off
cd cs695venv\Scripts && (
    activate && (
        cd.. && (
            cd.. && (
                jupyter notebook
            )
        )
    )
)
