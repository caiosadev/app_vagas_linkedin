import os
from dotenv import load_dotenv
import smtplib
from email.message import EmailMessage

load_dotenv('/Users/visuals/Downloads/app-linkedin/.env')

smtp_host = os.getenv('SMTP_HOST')
smtp_port = os.getenv('SMTP_PORT')
smtp_user = os.getenv('SMTP_USER')
smtp_pass = os.getenv('SMTP_PASS')

print("Using host:", smtp_host)

msg = EmailMessage()
msg['Subject'] = 'App Vagas - Teste de Envio via SendPulse'
msg['From'] = 'caio@visuals.com.br'
msg['To'] = 'caio@visuals.com.br'

msg.set_content('Teste de envio bem-sucedido!')
msg.add_alternative('''
<html>
<body>
    <h2 style="color: #0284c7;">A Plataforma de Vagas Agora Tem E-mail!</h2>
    <p>O envio via <b>SendPulse</b> está 100% configurado e funcional. O orquestrador agora tem passe livre para disparar os alertas de empregos diretamente para a caixa dos usuários.</p>
</body>
</html>
''', subtype='html')

try:
    with smtplib.SMTP(smtp_host, int(smtp_port)) as server:
        server.starttls()
        server.login(smtp_user, smtp_pass)
        server.send_message(msg)
    print("Email sent successfully!")
except Exception as e:
    print(f"Error: {e}")
