import rpyc


def main():
    try:
        sensei = rpyc.connect('localhost', 33333).root
        print("Successful connection!")

        sensei.diagnostic()
    except ConnectionRefusedError:
        print("Connection error!")


if __name__=='__main__':
    main()