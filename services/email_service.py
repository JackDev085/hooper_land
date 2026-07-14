import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os
from dotenv import load_dotenv
from typing import List

load_dotenv()


class EmailService:
    """
    Serviço de envio de emails para o Ballers085 App.
    Utiliza SMTP do Gmail para envio de emails em massa.
    """
    
    def __init__(self):
        self._email = os.getenv("EMAIL")
        self._password_app = os.getenv("PASSWORD_APP")
        
        if not self._email or not self._password_app:
            import logging
            logging.warning("EMAIL e PASSWORD_APP não configurados no .env. Funcionalidades de e-mail estarão desativadas.")
    
    @property
    def email(self) -> str:
        return self._email
    
    @property
    def password_app(self) -> str:
        return self._password_app
    
    def _create_reminder_message(self, to_email: str, to_name: str) -> MIMEMultipart:
        """
        Cria uma mensagem de lembrete de avaliação pré-treino.
        """
        subject = "🏀 Lembrete: Preencha sua avaliação no Ballers085"
        
        html_content = f"""
        <html>
        <head>
            <style>
                body {{
                    font-family: Arial, sans-serif;
                    background-color: #f4f4f4;
                    margin: 0;
                    padding: 0;
                }}
                .container {{
                    max-width: 600px;
                    margin: 0 auto;
                    background-color: #ffffff;
                    padding: 30px;
                    border-radius: 10px;
                    box-shadow: 0 2px 10px rgba(0,0,0,0.1);
                }}
                .header {{
                    text-align: center;
                    padding-bottom: 20px;
                    border-bottom: 2px solid #ff6b35;
                }}
                .header h1 {{
                    color: #ff6b35;
                    margin: 0;
                }}
                .content {{
                    padding: 20px 0;
                    color: #333;
                    line-height: 1.6;
                }}
                .cta-button {{
                    display: inline-block;
                    background-color: #ff6b35;
                    color: #ffffff !important;
                    padding: 12px 30px;
                    text-decoration: none;
                    border-radius: 5px;
                    font-weight: bold;
                    margin: 20px 0;
                }}
                .footer {{
                    text-align: center;
                    padding-top: 20px;
                    border-top: 1px solid #eee;
                    color: #888;
                    font-size: 12px;
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>🏀 Ballers085</h1>
                </div>
                <div class="content">
                    <p>Olá, <strong>{to_name}</strong>!</p>
                    
                    <p>Este é um lembrete para preencher sua <strong>avaliação pré-treino</strong> no aplicativo Ballers085.</p>
                    
                    <p>A sua avaliação é fundamental para:</p>
                    <ul>
                        <li>📊 Monitorar seu desempenho e evolução</li>
                        <li>💪 Ajustar a carga de treino adequadamente</li>
                        <li>🩺 Prevenir lesões e fadiga excessiva</li>
                        <li>📈 Acompanhar seu progresso ao longo do tempo</li>
                    </ul>
                    
                    <p>Leva apenas alguns segundos e faz toda a diferença no seu desenvolvimento!</p>
                    
                    <p style="text-align: center;">
                        <a href="https://ballers085.vercel.app" class="cta-button">Acessar o Aplicativo</a>
                    </p>
                    
                    <p>Conte com a gente para alcançar seus objetivos! 🚀</p>
                </div>
                <div class="footer">
                    <p>Este é um email automático enviado pelo sistema Ballers085.</p>
                    <p>© 2025 Ballers085 - Todos os direitos reservados.</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        text_content = f"""
        Olá, {to_name}!
        
        Este é um lembrete para preencher sua avaliação pré-treino no aplicativo Ballers085.
        
        A sua avaliação é fundamental para:
        - Monitorar seu desempenho e evolução
        - Ajustar a carga de treino adequadamente
        - Prevenir lesões e fadiga excessiva
        - Acompanhar seu progresso ao longo do tempo
        
        Leva apenas alguns segundos e faz toda a diferença no seu desenvolvimento!
        
        Acesse: https://ballers085.vercel.app
        
        Conte com a gente para alcançar seus objetivos!
        
        ---
        Este é um email automático enviado pelo sistema Ballers085.
        © 2025 Ballers085 - Todos os direitos reservados.
        """
        
        msg = MIMEMultipart("alternative")
        msg["Subject"] = subject
        msg["From"] = self._email
        msg["To"] = to_email
        
        part1 = MIMEText(text_content, "plain")
        part2 = MIMEText(html_content, "html")
        
        msg.attach(part1)
        msg.attach(part2)
        
        return msg
    
    def send_reminder_email(self, to_email: str, to_name: str) -> bool:
        """
        Envia um email de lembrete para um destinatário específico.
        """
        if not self._email or not self._password_app:
            raise ValueError("EMAIL e PASSWORD_APP devem estar configurados no .env para enviar e-mails")
        try:
            msg = self._create_reminder_message(to_email, to_name)
            
            with smtplib.SMTP("smtp.gmail.com", 587) as smtp:
                smtp.starttls()
                smtp.login(self._email, self._password_app)
                smtp.send_message(msg)
                
            print(f"✅ Email enviado com sucesso para {to_email}")
            return True
            
        except Exception as e:
            print(f"❌ Erro ao enviar email para {to_email}: {e}")
            raise Exception(f"Erro ao enviar email para {to_email}: {e}")

    def _create_password_reset_message(self, to_email: str, to_name: str, reset_link: str) -> MIMEMultipart:
        """
        Cria uma mensagem de e-mail para redefinição de senha.
        """
        subject = "🏀 Redefinição de Senha - Ballers085"
        
        html_content = f"""
        <html>
        <head>
            <style>
                body {{
                    font-family: Arial, sans-serif;
                    background-color: #f4f4f4;
                    margin: 0;
                    padding: 0;
                }}
                .container {{
                    max-width: 600px;
                    margin: 0 auto;
                    background-color: #ffffff;
                    padding: 30px;
                    border-radius: 10px;
                    box-shadow: 0 2px 10px rgba(0,0,0,0.1);
                }}
                .header {{
                    text-align: center;
                    padding-bottom: 20px;
                    border-bottom: 2px solid #10b981;
                }}
                .header h1 {{
                    color: #10b981;
                    margin: 0;
                }}
                .content {{
                    padding: 20px 0;
                    color: #333;
                    line-height: 1.6;
                }}
                .cta-button {{
                    display: inline-block;
                    background-color: #10b981;
                    color: #ffffff !important;
                    padding: 12px 30px;
                    text-decoration: none;
                    border-radius: 5px;
                    font-weight: bold;
                    margin: 20px 0;
                }}
                .footer {{
                    text-align: center;
                    padding-top: 20px;
                    border-top: 1px solid #eee;
                    color: #888;
                    font-size: 12px;
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>🏀 Ballers085</h1>
                </div>
                <div class="content">
                    <p>Olá, <strong>{to_name}</strong>!</p>
                    
                    <p>Você solicitou a redefinição de senha para a sua conta no Ballers085.</p>
                    
                    <p>Clique no botão abaixo para redefinir a sua senha. Este link expirará em <strong>15 minutos</strong> e pode ser usado apenas uma única vez:</p>
                    
                    <p style="text-align: center;">
                        <a href="{reset_link}" class="cta-button" style="color: #ffffff !important;">Redefinir Minha Senha</a>
                    </p>
                    
                    <p>Se você não fez esta solicitação, por favor ignore este email. Sua senha continuará segura.</p>
                </div>
                <div class="footer">
                    <p>Este é um email automático enviado pelo sistema Ballers085.</p>
                    <p>© 2025 Ballers085 - Todos os direitos reservados.</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        text_content = f"""
        Olá, {to_name}!
        
        Você solicitou a redefinição de senha para a sua conta no Ballers085.
        
        Acesse o link abaixo para redefinir a sua senha. Este link expirará em 15 minutos e pode ser usado apenas uma única vez:
        
        {reset_link}
        
        Se você não fez esta solicitação, por favor ignore este email. Sua senha continuará segura.
        
        ---
        Este é um email automático enviado pelo sistema Ballers085.
        © 2025 Ballers085 - Todos os direitos reservados.
        """
        
        msg = MIMEMultipart("alternative")
        msg["Subject"] = subject
        msg["From"] = self._email
        msg["To"] = to_email
        
        part1 = MIMEText(text_content, "plain")
        part2 = MIMEText(html_content, "html")
        
        msg.attach(part1)
        msg.attach(part2)
        
        return msg

    def send_password_reset_email(self, to_email: str, to_name: str, reset_link: str) -> bool:
        """
        Envia um email com o link de redefinição de senha.
        """
        if not self._email or not self._password_app:
            raise ValueError("EMAIL e PASSWORD_APP devem estar configurados no .env para enviar e-mails")
        try:
            msg = self._create_password_reset_message(to_email, to_name, reset_link)
            
            with smtplib.SMTP("smtp.gmail.com", 587) as smtp:
                smtp.starttls()
                smtp.login(self._email, self._password_app)
                smtp.send_message(msg)
                
            print(f"✅ Email de redefinição enviado com sucesso para {to_email}")
            return True
            
        except Exception as e:
            print(f"❌ Erro ao enviar email de redefinição para {to_email}: {e}")
            raise Exception(f"Erro ao enviar email de redefinição para {to_email}: {e}")
    
    def send_bulk_reminder_emails(self, recipients: List[dict]) -> dict:
        """
        Envia emails de lembrete para múltiplos destinatários.
        """
        results = {
            "total": len(recipients),
            "success": 0,
            "failed": 0,
            "errors": []
        }
        
        for recipient in recipients:
            try:
                self.send_reminder_email(recipient["email"], recipient["name"])
                results["success"] += 1
            except Exception as e:
                results["failed"] += 1
                results["errors"].append({
                    "email": recipient["email"],
                    "error": str(e)
                })
        
        print(f"📧 Envio em massa concluído: {results['success']}/{results['total']} enviados com sucesso")
        return results


# Instância singleton do serviço
email_service = EmailService()
