import os
import mel_parser


def main():
    prog = '''
            
            Dim s As int = 3
            Dim s = 4
    
            if (a>5) then
                Dim s = 3
            else 
                Dim s As int = 3
            end if  
    '''
    prog = mel_parser.parse(prog)
    print(*prog.tree, sep=os.linesep)


if __name__ == "__main__":
    main()
