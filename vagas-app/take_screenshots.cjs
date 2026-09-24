const { chromium } = require('playwright');

(async () => {
  const browser = await chromium.launch({ headless: true });
  const context = await browser.newContext({ viewport: { width: 1280, height: 800 } });
  const page = await context.newPage();

  console.log("Acessando a aplicação...");
  await page.goto('http://localhost:5173');
  await page.waitForTimeout(3000); // Wait for load

  // The Auth Modal is open by default since we are not logged in.
  // Click the 'Cadastre-se' button to show the registration form
  console.log("Trocando para tela de cadastro...");
  await page.click('.auth-switch button');
  await page.waitForTimeout(500);

  console.log("Tirando print do Cadastro/Perfil...");
  await page.screenshot({ path: 'public/print-perfil.png' });

  console.log("Simulando login...");
  await page.evaluate(() => {
    localStorage.setItem('user', JSON.stringify({ name: 'Visuals', id: 1, email: 'teste@visuals.com.br' }));
    localStorage.setItem('token', 'fake-token-123');
    window.location.reload();
  });
  
  // Wait for the page to load after the hard reload
  await page.waitForTimeout(3000);

  // Now we should be on the main panel without the login modal
  console.log("Tirando print do Painel Principal...");
  await page.screenshot({ path: 'public/print-painel.png' });

  // Open Profile (where user uploads CV)
  console.log("Abrindo área de Currículo/Perfil logado...");
  try {
    await page.click('button.profile-action-btn', { force: true });
    await page.waitForTimeout(1000);
    console.log("Tirando print da área de currículo...");
    await page.screenshot({ path: 'public/print-curriculo.png' });
    
    // Close it
    const closeBtn = await page.$('.modal-overlay:not(.auth-overlay) .close-btn');
    if (closeBtn) {
      await closeBtn.click();
      await page.waitForTimeout(1000);
    } else {
      await page.keyboard.press('Escape');
      await page.waitForTimeout(1000);
    }
  } catch (err) {
    console.log("Erro ao abrir currículo: ", err);
  }

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
