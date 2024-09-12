import os
import platform

class SimpleLangCompiler:
    def __init__(self):
        self.variables = {}

    def parse(self, code):
        instructions = code.strip().split('\n')
        asm_code = []

        if platform.system() == 'Windows':
            asm_code.append(".data")
            asm_code.append("fmt db '%d', 0")
            asm_code.append(".bss")
            for line in instructions:
                if line.startswith("SET"):
                    _, var, value = line.split()
                    self.variables[var] = value
                    asm_code.append(f"{var} resd 1")
                elif line.startswith("ADD"):
                    _, var1, var2, result = line.split()
                    asm_code.append(f"mov eax, {var1}")
                    asm_code.append(f"add eax, {var2}")
                    asm_code.append(f"mov {result}, eax")
                elif line.startswith("PRINT"):
                    _, var = line.split()
                    asm_code.append(f"mov eax, {var}")
                    asm_code.append("mov edx, eax")
                    asm_code.append("mov ecx, fmt")
                    asm_code.append("mov ebx, 1")
                    asm_code.append("mov eax, 4")
                    asm_code.append("int 0x80")
                else:
                    raise ValueError(f"Unknown instruction: {line}")

            asm_code.append("mov eax, 1")
            asm_code.append("xor ebx, ebx")
            asm_code.append("int 0x80")
        
        elif platform.system() == 'Darwin':  # macOS
            asm_code.append(".data")
            asm_code.append("fmt: .asciz \"%d\\n\"")
            asm_code.append(".bss")
            for line in instructions:
                if line.startswith("SET"):
                    _, var, value = line.split()
                    self.variables[var] = value
                    asm_code.append(f"{var}: .space 4")
                elif line.startswith("ADD"):
                    _, var1, var2, result = line.split()
                    asm_code.append(f"mov rax, [{var1}]")
                    asm_code.append(f"add rax, [{var2}]")
                    asm_code.append(f"mov [{result}], rax")
                elif line.startswith("PRINT"):
                    _, var = line.split()
                    asm_code.append(f"mov rdi, fmt")
                    asm_code.append(f"mov rsi, [{var}]")
                    asm_code.append("mov rax, 1")
                    asm_code.append("mov rdi, 1")
                    asm_code.append("mov rdx, 4")
                    asm_code.append("syscall")
                else:
                    raise ValueError(f"Unknown instruction: {line}")

            asm_code.append("mov eax, 60")
            asm_code.append("xor edi, edi")
            asm_code.append("syscall")

        elif platform.system() == 'Linux':  # Linux
            asm_code.append("section .data")
            asm_code.append("fmt db '%d', 10, 0")
            asm_code.append("section .bss")
            for line in instructions:
                if line.startswith("SET"):
                    _, var, value = line.split()
                    self.variables[var] = value
                    asm_code.append(f"{var} resd 1")
                elif line.startswith("ADD"):
                    _, var1, var2, result = line.split()
                    asm_code.append(f"mov eax, [{var1}]")
                    asm_code.append(f"add eax, [{var2}]")
                    asm_code.append(f"mov [{result}], eax")
                elif line.startswith("PRINT"):
                    _, var = line.split()
                    asm_code.append(f"mov eax, [{var}]")
                    asm_code.append("mov rdi, fmt")
                    asm_code.append("mov rsi, rax")
                    asm_code.append("mov rax, 1")
                    asm_code.append("mov rdi, 1")
                    asm_code.append("mov rdx, 4")
                    asm_code.append("syscall")
                else:
                    raise ValueError(f"Unknown instruction: {line}")

            asm_code.append("mov eax, 60")
            asm_code.append("xor edi, edi")
            asm_code.append("syscall")

        return '\n'.join(asm_code)

    def compile_and_run(self, code):
        asm_code = self.parse(code)

        # Write assembly code to a file
        with open('program.asm', 'w') as f:
            f.write(asm_code)

        if platform.system() == 'Windows':
            # Assemble and link for Windows
            os.system('ml64 /c /Foprogram.obj program.asm')
            os.system('link /OUT:program.exe program.obj')
            os.system('program.exe')
        
        elif platform.system() == 'Darwin':  # macOS
            # Assemble and link for macOS
            os.system('nasm -f macho64 program.asm -o program.o')
            os.system('ld -o program program.o -macosx_version_min 10.7 -lSystem')
            os.system('./program')

        elif platform.system() == 'Linux':
            # Assemble and link for Linux
            os.system('nasm -f elf64 program.asm -o program.o')
            os.system('ld program.o -o program')
            os.system('./program')

# Example usage
code = """
SET x 10
SET y 20
ADD x y z
PRINT z
"""

compiler = SimpleLangCompiler()
compiler.compile_and_run(code)
