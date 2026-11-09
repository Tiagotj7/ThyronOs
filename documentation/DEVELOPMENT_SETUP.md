# Preparação do ambiente de desenvolvimento

## Regra

O host do desenvolvedor ainda não foi confirmado. Não instale dependências nem execute comandos de alteração antes de coletar o diagnóstico e revisar os resultados.

## Diagnóstico somente leitura

```bash
echo "===== SISTEMA OPERACIONAL ====="
cat /etc/os-release
echo
echo "===== ARQUITETURA ====="
uname -m
echo
echo "===== PROCESSADOR ====="
lscpu | grep -E 'Model name|CPU\(s\)'
echo
echo "===== MEMÓRIA ====="
free -h
echo
echo "===== ARMAZENAMENTO ====="
df -hT
echo
echo "===== DISCOS E PARTIÇÕES ====="
lsblk -o NAME,SIZE,TYPE,FSTYPE,MOUNTPOINTS
echo
echo "===== GERENCIADORES DE PACOTES ====="
command -v apt
command -v dnf
command -v pacman
command -v zypper
echo
echo "===== FERRAMENTAS ====="
git --version
python3 --version
```

## Depois do diagnóstico

A preparação deve considerar a distribuição real do host, espaço livre, arquitetura e disponibilidade de virtualização. Priorizar ambiente isolado para build e VM para testes. Não substituir o sistema instalado pelo Kali apenas para desenvolver o THYRON OS.
