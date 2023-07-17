import subprocess
from subprocess import CalledProcessError
import asyncio
import html






class TerminalResponse:

    
    
    
    @classmethod
    async def new(cls, command: str) -> str:
        try:
            proc = await asyncio.create_subprocess_shell(
                command,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                shell=True,
            )
            stdout, _ = await proc.communicate()
            resp = html.escape(stdout.decode('latin-1'))

        except (
            FileNotFoundError,
            CalledProcessError,        
        ) as e:
            resp = str(e)
        

        return resp
    