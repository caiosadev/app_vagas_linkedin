const { chromium } = require('playwright');

(async () => {
  const browser = await chromium.launch({ headless: true });
  const context = await browser.newContext({ viewport: { width: 1280, height: 800 } });
  const page = await context.newPage();

  console.log("Acessando a aplicação...");
  await page.goto('http://localhost:5173');
  await page.waitForTimeout(3000); // Wait for load

  // The Auth Modal might be open by default if not logged in.
  console.log("Tirando print do Perfil/Login...");
  await page.screenshot({ path: 'public/print-perfil.png' });

  // Close the Auth Modal by pressing Escape or clicking outside
  console.log("Fechando modal de login...");
  await page.keyboard.press('Escape');
  await page.waitForTimeout(1000);
  
  // Just in case it didn't close, try clicking the close button if it exists
  const closeBtn = await page.$('.modal-overlay.auth-overlay .close-btn');
  if (closeBtn) {
    await closeBtn.click();
    await page.waitForTimeout(1000);
  } else {
    // If no close button, try clicking the overlay background to close
    await page.mouse.click(10, 10);
    await page.waitForTimeout(1000);
  }

  // Now we should be on the main panel
  console.log("Tirando print do Painel Principal...");
  await page.screenshot({ path: 'public/print-painel.png' });

  // Open Newsletter
  console.log("Abrindo Newsletter...");
  try {
    await page.click('button.newsletter-btn', { force: true });
    await page.waitForTimeout(1500);
    console.log("Tirando print da Newsletter...");
    await page.screenshot({ path: 'public/print-newsletter.png' });
  } catch (err) {
    console.log("Erro ao abrir newsletter: ", err);
  }

  await browser.close();
  console.log("Prints salvos com sucesso na pasta public!");
})();
