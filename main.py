import os
import mel_parser


def main():
    prog = '''
        void myFunc(int[] a, boolean b) {
            for s As int = 3 To 5 
            Dim s As int = 3
            Dim s As int = 3
            Dim s As int = 3
            Next s
            
            if (a>5) then
                Dim s As int = 3
            else 
                Dim s As int = 3
            end if  
            
            while (a>5) 
                Dim s As int = 3
            end while                 
            
            do while (a>5) 
                Dim s As int = 3
            Loop
        }
    
    '''
    prog = mel_parser.parse(prog)
    print(*prog.tree, sep=os.linesep)


if __name__ == "__main__":
    main()
