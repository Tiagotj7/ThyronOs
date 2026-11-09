# Plano de testes

## Matriz mínima por build Live

| Área | Verificação | Evidência |
|---|---|---|
| Boot | ISO inicia em VM | Captura/log e configuração da VM |
| Sessão | GNOME abre | Resultado e versão GNOME |
| Identidade | Wallpaper/tema aplicados | Captura de tela |
| Entrada | Teclado e mouse | Resultado |
| Rede | Interface e conectividade | Resultado sem expor dados privados |
| Aplicativos | Aplicativos essenciais abrem | Lista e observações |
| Estabilidade | Sem falha crítica durante sessão | Duração e logs |
| Encerramento | Sistema encerra corretamente | Resultado |
| Recursos | RAM/CPU em repouso | Medição e configuração da VM |

## Ambiente de teste

Registrar:
- identificador do build;
- hash SHA-256 da ISO;
- versão Kali e GNOME;
- hipervisor e versão;
- RAM, CPU, firmware e disco virtual;
- data do teste.

## Resultado

Use **Passou**, **Falhou**, **Não testado** ou **Não aplicável**. Não marque como passou sem evidência. Falhas devem gerar Issue com passos de reprodução e logs sanitizados.
