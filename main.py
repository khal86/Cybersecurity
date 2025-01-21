import os
import subprocess
import sys
import random
import string
from cryptography.fernet import Fernet
import stdiomask


def generateMasterPassword():
    key = Fernet.generate_key()
    with open("./master.key", "wb") as masterPasswordWriter:
        masterPasswordWriter.write(key)

def loadMasterPassword():
    try:
        with open("./master.key", "rb") as keyFile:
            return keyFile.read()
    except FileNotFoundError:
        print("Erreur : le fichier master.key est introuvable.")
        sys.exit()

def createVault():
    with open("./vault.txt", "wb") as vault:
        vault.write(b"")

def encryptData(data):
    f = Fernet(loadMasterPassword())
    try:
        with open("./vault.txt", "rb") as vaultReader:
            encryptedData = vaultReader.read()
        if not encryptedData:
            return f.encrypt(data.encode())
        else:
            decryptedData = f.decrypt(encryptedData)
            newData = decryptedData.decode() + data
            return f.encrypt(newData.encode())
    except Exception as e:
        print(f"Erreur lors du chiffrement des données : {e}")
        sys.exit()

def decryptData(encryptedData):
    f = Fernet(loadMasterPassword())
    try:
        return f.decrypt(encryptedData)
    except Exception as e:
        print(f"Erreur lors du déchiffrement des données : {e}")
        sys.exit()

def appendNewPassword():
    print()
    userName = input("Veuillez entrer un nom d'utilisateur : ")
    password = stdiomask.getpass(prompt= "Veuillez entrer le mot de passe : " ,mask = "*")
    website = input("Veuillez entrer l'adresse du site web : ")
    print()
    
    userNameLine = f"Nom d'utilisateur : {userName}\n"
    passwordLine = f"Mot de passe : {password}\n"
    websiteLine = f"Site web : {website}\n\n"
    
    encryptedData = encryptData(userNameLine + passwordLine + websiteLine)
    with open("./vault.txt", "wb") as vaultWriter:
        vaultWriter.write(encryptedData)

def readPasswords():
    try:
        with open("vault.txt", "rb") as passwordsReader: 
            encryptedData = passwordsReader.read()
        print()
        print(decryptData(encryptedData).decode())
    except FileNotFoundError:
        print("Erreur : le fichier vault.txt est introuvable.")
    except Exception as e:
        print(f"Erreur lors de la lecture des mots de passe : {e}")

def generateNewPassword(passwordLength):
    randomString = string.ascii_letters + string.digits + string.punctuation
    newPassword = ''.join(random.choice(randomString) for _ in range(passwordLength))
    print()
    print(f"Voici votre mot de passe : {newPassword}")

# Partie principale du programme 
subprocess.call('clear', shell=True)

print("-" * 60)
print("Bienvenue dans le gestionnaire de mots de passe ! ")
print("-" * 60)

if os.path.exists("./vault.txt") and os.path.exists("./master.key"):
    print("Vous pouvez sélectionner l'une des options suivantes : ")
    print("1 - Sauvegarder un nouveau mot de passe ")
    print("2 - Générer un nouveau mot de passe aléatoire")
    print("3 - Obtenir la liste de vos mots de passe")
    
    userChoice = input("Que souhaitez-vous faire ? (1/2/3) ")
    if userChoice == "1":
        appendNewPassword()
    elif userChoice == "2":
        passwordLength = input("Quelle est la longueur du mot de passe ? ")
        if passwordLength.isdigit():
            generateNewPassword(int(passwordLength))
        else:
            print("Merci de rentrer un nombre valide la prochaine fois...")
            sys.exit()
    elif userChoice == "3":
        readPasswords()
    else:
        print("L'option sélectionnée n'existe pas ...")
        sys.exit()
else:
    print("Génération d'un mot de passe maître et d'un coffre de mots de passe ... ")
    generateMasterPassword()
    createVault()
    print("Génération terminée, veuillez relancer le programme.")
