# Matrice de Sécurité - Projet Sentinel-X

| Mesure de Sécurité | Composant / Cible | État / Implémentation |
|---|---|---|
| Chiffrement TLS 1.3 | Serveur MQTT (Mosquitto) | Activé sur le port 8883 avec TLS_AES_256_GCM_SHA384 |
| Authentification | Mosquitto MQTT | Obligatoire (Utilisateur `sentinel`, refus des connexions anonymes) |
| Durcissement Conteneur | Docker / Mosquitto | Exécution sous un utilisateur non-root (1883:1883) |
| Protection des Fichiers | Clés et Passwords | Permissions restreintes (chmod 600 sur `server.key` et `passwordfile`) |
| Filtrage Réseau | Pare-feu Windows | Ports non sécurisés bloqués, port 8883 autorisé |
| Validation & Audit | Nmap / OpenSSL | Testé et vérifié (Ciphers Grade A, TLS 1.3 validé) |
