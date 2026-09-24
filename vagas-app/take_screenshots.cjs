const { chromium } = require('playwright');

(async () => {
  const browser = await chromium.launch({ headless: true });
  const context = await browser.newContext({ viewport: { width: 1280, height: 800 } });
  const page = await context.newPage();

  console.log("Acessando a aplicação...");
  await page.goto('http://localhost:5173');
  await page.waitForTimeout(2000); // Wait for animations and data to load

  // 1. Painel Principal
  console.log("Tirando print do Painel Principal...");
  await page.screenshot({ path: 'public/print-painel.png' });

  // 2. Perfil
  console.log("Abrindo Perfil...");
  await page.click('button.profile-action-btn');
  await page.waitForTimeout(1000);
  console.log("Tirando print do Perfil...");
  await page.screenshot({ path: 'public/print-perfil.png' });

  // Close profile
  await page.click('button.close-btn');
  await page.waitForTimeout(1000);

  // 4. Receber vagas por E-mail
  console.log("Abrindo Newsletter...");
  await page.click('button.newsletter-btn');
  await page.waitForTimeout(1000);
  console.log("Tirando print da Newsletter...");
  await page.screenshot({ path: 'public/print-newsletter.png' });

  await browser.close();
  console.log("Prints salvos com sucesso na pasta public!");
})();
