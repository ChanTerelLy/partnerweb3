from django.test import TestCase

# Create your tests here.
class Multi:
    def imeth(self, x):
        print (self, x)

    def smeth(x):
        print (x)

    def cmeth(cls, x):
        print (cls, x)

    smeth = staticmethod(smeth)
    cmeth = classmethod(cmeth)

if __name__ == "__main__":
    m = Multi()
    print(Multi.smeth(3))

