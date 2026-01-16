import socket
from cryptography.fernet import Fernet
from time import sleep
import struct
import base64
from threading import Thread
#create first server socket
me=socket.socket()
#bind your ip to the port
me.bind(('localhost',9999))
me.listen(1)
c1,addr=me.accept()
#generate an encryption key 
key1=Fernet.generate_key()
c1.send(key1)
#receive peer's encryption key
key2=bytes(c1.recv(1024).decode(),'utf-8')
#use the first half of your key and the second half of
#the peer's key for encryption
#Use the remaining half for decryption
my_key=bytes(key1[0:len(key1)//2]+key2[len(key2)//2:])
peer_key=bytes(key2[0:len(key2)//2]+key1[len(key1)//2:])
class receiving(Thread):
    #The decryption function takes the cipher text as an argument
    def decryption(self):
        # Read 4-byte length header
        raw_len = recv_exact(c1, 4)
        length = struct.unpack('!I', raw_len)[0]
        # Read full encrypted token
        token = recv_exact(c1, length)
        # Fernet decrypt
        decrypted = Fernet(peer_key).decrypt(token)
        # Base64 decode → original bytes
        return base64.b64decode(decrypted)
    def receive(self):
        try:
            #if the message has a special function
            name=self.decryption().decode()
            f1=open(name,'wb')
            #only audio, video, and images are encrypted, hence, decryption follows the same way
            if self.msg.decode() == '*img*' or self.msg.decode()=='*aud*' or self.msg.decode()=='*vid*':
                decoded_chunk=self.decryption()
                while decoded_chunk!=b'*end*':
                    f1.write(decoded_chunk)
                    decoded_chunk=self.decryption()
            else:
                decoded_chunk=base64.b64decode(c1.recv(self.byte_size))
                while decoded_chunk!=b'*end*':
                    f1.write(decoded_chunk)
                decoded_chunk=base64.b64decode(c1.recv(self.byte_size))
            print('Received')
            f1.close()
        except ConnectionResetError:
            print('Client disconnected')
    def run(self):
        while True:
            try:
                #receive the encrypted message 
                self.msg=self.decryption()
                #checks if the message is a keyword
                if self.msg.decode()=='*img*':
                    print('Incoming image')
                    self.receive()
                elif self.msg.decode()=='*aud*':
                    print('Incoming audio')
                    self.receive()
                elif self.msg.decode()=='*vid*':
                    print('Incoming video')
                    self.receive()
                elif self.msg.decode()=='*oth*':
                    print('Type shii file incoming')
                elif self.msg.decode()=='*term*':
                    c1.close()
                else:
                    #if the message has no special function, it prints it
                    print(self.msg.decode())
            except ConnectionResetError:
                break
            except OSError:
                break
class sending(Thread):
    def encryption(self, content):
        # Base64 encode
        b64 = base64.b64encode(content)
        # Fernet encrypt
        token = Fernet(my_key).encrypt(b64)
        # Frame: 4-byte length prefix
        header = struct.pack('!I', len(token))
        # Send atomically
        c1.sendall(header + token)
    def send(self):
        file_status=False
        #wrong file name can only be supplied thrice
        #breaks at the third one
        for i in range(3):
            try:
                #Try to open the file with the file name supplied
                name=input('Enter file name ')
                f1=open(name,'rb')
                #if file name is valid, set this variable to true
                file_status=True
                break
            #if file isn't found, tell the user and continue to the next iteration 
            except FileNotFoundError:
                print('Please input a valid file name')
        if file_status:
            self.encryption(bytes(self.msg,'utf-8'))
            sleep(0.5)
            #send the file name
            self.encryption(bytes(name,'utf-8'))
               #ISO, OVA etc are too large and don't need to be encrypted,
               #encrypt just images, videos and audios
            if self.msg=='*img*'or self.msg=='*aud*' or self.msg=='*vid*':
                chunk=f1.read(self.block_bytes)
                while chunk:
                    #encrypt the encoded file chunks before sending
                    self.encryption(chunk)
                    chunk=f1.read(self.block_bytes)
            else:
                #just read and encode in b64, no encryption, just 1 layer of security
                chunk=f1.read(self.block_bytes)
                while chunk:
                    encoded=base64.b64encode(chunk)
                    c1.send(encoded)
                    chunk=f1.read(self.block_bytes)
            self.encryption(bytes('*end*','utf-8'))
            print('Sent')
            f1.close()
    def run(self):
        print('INPUT YOUR MSG: ')
        while True:
            try:
                #collect the input message
                self.msg=input()
                #Checks the type of file to be sent based on the key words
                if self.msg=='*img*':
                    self.file,self.block_bytes='image',3*512
                    self.send()
                elif self.msg=='*vid*':
                    self.file,self.block_bytes='video',3*1024
                    self.send()
                elif self.msg=='*aud*':
                    self.file,self.block_bytes='audio',3*1024
                    self.send()
                elif self.msg=='*oth*':
                    self.file,self.block_bytes='other',3*1024*1024
                    self.send()
                elif self.msg=='*term*':
                    #If message equal to *term*, call the encryption function and break the loop
                    self.encryption(bytes(self.msg,'utf-8'))
                    c1.close()
                    break
                else:
                    #If message isn't equal to any keyword, call the encryption function 
                    self.encryption((bytes(self.msg,'utf-8')))
            except ConnectionResetError:
                print('Disconnected')
                break
def recv_exact(sock, n):
    data = b''
    while len(data) < n:
        chunk = sock.recv(n - len(data))
        if not chunk:
            raise ConnectionResetError
        data += chunk
    return data
obj1=receiving()
obj2=sending()
obj1.start()
obj2.start()