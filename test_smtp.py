import smtplib
from email.message import EmailMessage

msg = EmailMessage()
msg.set_content("Teste de SMTP!")
msg['Subject'] = 'Teste'
msg['From'] = 'appvagas@visuals.com.br'
msg['To'] = 'trezzde@gmail.com'

try:
    with smtplib.SMTP('mail.visuals.com.br', 587) as server:
        server.starttls()
        server.login('appvagas@visuals.com.br', 'ubaCflCqmHhq+{Ar')
        server.send_message(msg)
    print("Sucesso!")
except Exception as e:
    print(f"Erro: {e}")
