const path = require('path');
const crypto = require('crypto');
const express = require('express');
const sql = require('mssql');
const nodemailer = require('nodemailer');
const bcrypt = require('bcrypt');

const app = express();
const port = process.env.PORT || 3000;
const publicHost = process.env.PUBLIC_URL || `http://100.99.13.22:${port}`;
const apiVersion = '1.7.7';

// FIX: suppression de la référence à `host` qui n'était pas défini (ReferenceError)
const dbConfig = {
  user: process.env.DB_USER,
  password: process.env.DB_PASSWORD,
  server: process.env.DB_SERVER,
  database: process.env.DB_DATABASE || 'WEB_NATHANAEL',
  port: process.env.DB_PORT ? parseInt(process.env.DB_PORT, 10) : 1433,
  options: {
    encrypt: false,
    trustServerCertificate: true
  }
};

const pool = new sql.ConnectionPool(dbConfig);
const poolConnect = pool.connect();

poolConnect.then(() => {
  console.log('✅ Connexion réussie à SQL Server sur :', dbConfig.server);
}).catch(err => {
  console.error('❌ Erreur de connexion à la base de données :', err.message);
});

pool.on('error', err => {
  console.error('SQL Pool Error:', err);
});

// Sessions en mémoire : token -> { username, role }
const sessions = new Map();

function generateToken() {
  return crypto.randomBytes(32).toString('hex');
}

function escapeHtml(str) {
  return String(str ?? '')
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#039;');
}

function authMiddleware(req, res, next) {
  const token = (req.headers['authorization'] || '').replace('Bearer ', '');
  if (!token || !sessions.has(token)) {
    return res.status(401).json({ error: 'Non authentifié.' });
  }
  req.session = sessions.get(token);
  next();
}

function adminMiddleware(req, res, next) {
  const token = (req.headers['authorization'] || '').replace('Bearer ', '');
  if (!token || !sessions.has(token)) {
    return res.status(401).json({ error: 'Non authentifié.' });
  }
  const session = sessions.get(token);
  if (session.role !== 'Admin') {
    return res.status(403).json({ error: 'Accès refusé. Réservé aux administrateurs.' });
  }
  req.session = session;
  next();
}

// CORS — autorise le header Authorization pour les tokens de session
app.use((req, res, next) => {
  res.header('Access-Control-Allow-Origin', '*');
  res.header('Access-Control-Allow-Headers', 'Origin, X-Requested-With, Content-Type, Accept, Authorization');
  res.header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS');
  if (req.method === 'OPTIONS') return res.sendStatus(200);
  next();
});

app.use(express.json());

app.use((req, res, next) => {
  console.log(`[${new Date().toISOString()}] ${req.method} ${req.url}`);
  next();
});

app.get('/api/info', (req, res) => {
  res.json({ version: apiVersion, status: 'running' });
});

app.get('/api/verify-session', authMiddleware, (req, res) => {
  res.json({ valid: true, username: req.session.username, role: req.session.role });
});

app.post('/api/logout', (req, res) => {
  const token = (req.headers['authorization'] || '').replace('Bearer ', '');
  if (token) sessions.delete(token);
  res.json({ message: 'Déconnecté.' });
});

// Configuration Nodemailer
const transporter = nodemailer.createTransport({
  service: 'gmail',
  auth: {
    user: 'oldvivaldi@gmail.com',
    pass: process.env.EMAIL_PASSWORD
  }
});

transporter.verify((error) => {
  if (error) {
    console.error('❌ Erreur configuration SMTP (Gmail) :', error.message);
  } else {
    console.log('✅ Serveur de mail prêt à envoyer des messages');
  }
});

async function sendResetEmail(login, email, customSubject = null) {
  const userMailOptions = {
    from: '"administrateur" <oldvivaldi@gmail.com>',
    to: email,
    subject: customSubject || 'Action requise : Définissez votre mot de passe - Nathanaël',
    html: `
      <h3>Bonjour ${login},</h3>
      <p>Une action est requise sur votre compte pour définir ou réinitialiser votre mot de passe.</p>
      <p>Veuillez cliquer sur le bouton ci-dessous pour accéder à la page sécurisée :</p>
      <a href="${publicHost}/reset-password.html?login=${encodeURIComponent(login)}"
         style="background-color: #007bff; color: white; padding: 12px 24px; text-decoration: none; border-radius: 8px; display: inline-block; font-weight: bold;">
         Définir mon mot de passe
      </a>
      <p>Si vous n'êtes pas à l'origine de cette demande, vous pouvez ignorer cet e-mail.</p>
      <p>Cordialement,<br>L'équipe de Nathanaël.</p>
    `
  };
  return transporter.sendMail(userMailOptions);
}

app.get('/api/buttons', async (req, res) => {
  try {
    await poolConnect;
    const result = await pool.request()
      .query(`
        SELECT ButtonKey, ButtonText, CONVERT(VARCHAR(19), last_change_date, 120) AS last_change_date
        FROM SiteButtons
        ORDER BY ButtonKey
      `);
    res.json(result.recordset);
  } catch (error) {
    console.error('API /api/buttons error:', error);
    res.status(500).json({ error: 'Impossible de charger les libellés de boutons.' });
  }
});

// Protégé admin
app.post('/api/buttons', adminMiddleware, async (req, res) => {
  const buttons = Array.isArray(req.body) ? req.body : [req.body];

  try {
    await poolConnect;
    const transaction = new sql.Transaction(pool);
    await transaction.begin();

    try {
      for (const btn of buttons) {
        await transaction.request()
          .input('key', sql.NVarChar, btn.ButtonKey)
          .input('text', sql.NVarChar, btn.ButtonText)
          .query(`
            MERGE INTO SiteButtons AS target
            USING (SELECT @key AS ButtonKey, @text AS ButtonText) AS source
            ON (target.ButtonKey = source.ButtonKey)
            WHEN MATCHED THEN
                UPDATE SET ButtonText = source.ButtonText, last_change_date = CAST(GETDATE() AS DATETIME2(0))
            WHEN NOT MATCHED THEN
                INSERT (ButtonKey, ButtonText, last_change_date) VALUES (source.ButtonKey, source.ButtonText, CAST(GETDATE() AS DATETIME2(0)));
          `);
      }
      await transaction.commit();
      res.json({ message: `${buttons.length} bouton(s) synchronisé(s) avec succès.` });
    } catch (err) {
      await transaction.rollback();
      throw err;
    }
  } catch (error) {
    console.error('API /api/buttons POST error:', error);
    res.status(500).json({ error: 'Erreur lors de la synchronisation des données.' });
  }
});

app.post('/api/login', async (req, res) => {
  const { username, password } = req.body;

  if (!username) {
    return res.status(400).json({ error: "Nom d'utilisateur requis." });
  }

  try {
    await poolConnect;
    const result = await pool.request()
      .input('username', sql.NVarChar, username.trim())
      .query('SELECT UserID, Username, Email, Role, MustResetPassword, MotDePasseIsActive, PasswordHash FROM Utilisateurs WHERE Username = @username');

    if (result.recordset.length === 0) {
      return res.status(401).json({ error: 'Utilisateur non reconnu.' });
    }

    const user = result.recordset[0];

    if (user.MotDePasseIsActive) {
      // Compte actif : mot de passe obligatoire pour tous les utilisateurs
      if (!password) {
        return res.status(400).json({ error: 'Mot de passe requis.' });
      }
      try {
        const match = await bcrypt.compare(password, user.PasswordHash);
        if (!match) {
          return res.status(401).json({ error: 'Identifiant ou mot de passe incorrect.' });
        }
      } catch (bcryptError) {
        console.error('Erreur bcrypt (hash invalide ?):', bcryptError.message);
        return res.status(401).json({ error: 'Identifiant ou mot de passe incorrect.' });
      }
    } else {
      // Compte non activé : seul l'Admin peut se connecter sans mot de passe
      if (user.Role !== 'Admin') {
        return res.status(401).json({ error: "Compte en attente d'activation. Veuillez patienter." });
      }
    }

    const token = generateToken();
    sessions.set(token, { username: user.Username, role: user.Role || 'User' });

    // On ne renvoie jamais le hash du mot de passe au client
    const { PasswordHash, ...safeUser } = user;
    res.json({ ...safeUser, token });
  } catch (error) {
    console.error('API /api/login error:', error);
    res.status(500).json({ error: "Erreur lors de la vérification de l'utilisateur." });
  }
});

app.post('/api/reset-password', async (req, res) => {
  const { login, password } = req.body;

  if (!login || !password) {
    return res.status(400).json({ error: 'Login et mot de passe requis.' });
  }

  const cleanLogin = login.trim();

  try {
    await poolConnect;
    const saltRounds = 10;
    const hashedPassword = await bcrypt.hash(password, saltRounds);

    const result = await pool.request()
      .input('login', sql.NVarChar, cleanLogin)
      .input('hash', sql.NVarChar, hashedPassword)
      .query(`
        UPDATE [dbo].[Utilisateurs]
        SET PasswordHash = @hash, MustResetPassword = 0, MotDePasseIsActive = 1
        WHERE Username = @login
      `);

    if (result.rowsAffected[0] === 0) {
      console.error(`[Reset] Échec: Aucun utilisateur trouvé avec le login "${cleanLogin}"`);
      return res.status(404).json({ error: "Utilisateur non trouvé. Le lien est peut-être expiré ou erroné." });
    }

    console.log(`[Reset] Mot de passe mis à jour pour: ${cleanLogin}`);
    res.json({ message: 'Mot de passe mis à jour avec succès.' });
  } catch (error) {
    console.error('API /api/reset-password error:', error);
    res.status(500).json({ error: 'Erreur lors de la mise à jour du mot de passe.' });
  }
});

app.post('/api/activate', async (req, res) => {
  const { login, email } = req.body;

  if (!login || !email) {
    return res.status(400).json({ error: 'Login et email requis.' });
  }

  try {
    await poolConnect;
    const checkUser = await pool.request()
      .input('login', sql.NVarChar, login)
      .query('SELECT UserID FROM Utilisateurs WHERE Username = @login');

    if (checkUser.recordset.length > 0) {
      return res.status(409).json({ error: 'Cet identifiant est déjà utilisé ou en attente.' });
    }

    // MotDePasseIsActive = 0 : le compte est inactif jusqu'à ce que l'utilisateur
    // définisse son mot de passe via le lien de réinitialisation
    await pool.request()
      .input('login', sql.NVarChar, login)
      .input('email', sql.NVarChar, email)
      .query(`
        INSERT INTO [dbo].[Utilisateurs]
          (Username, Email, PasswordHash, Role, MustResetPassword, MotDePasseIsActive, UserCreatedBy, LastModificationUserBy)
        VALUES
          (@login, @email, 'WAITING_FOR_HASH', 'User', 0, 0, @login, @login)
      `);

    console.log(`Utilisateur ${login} inséré en base (en attente).`);

    const adminMailOptions = {
      from: 'oldvivaldi@gmail.com',
      to: 'oldvivaldi@gmail.com',
      subject: `Demande d'activation de compte : ${login}`,
      html: `
        <h3>Nouvelle demande d'activation</h3>
        <p>L'utilisateur <strong>${escapeHtml(login)}</strong> (${escapeHtml(email)}) souhaite activer son compte.</p>
        <p>Cliquez sur le bouton ci-dessous pour valider sa demande et lui envoyer le lien de création de mot de passe :</p>
        <a href="${publicHost}/api/confirm-activation?login=${encodeURIComponent(login)}&email=${encodeURIComponent(email)}"
           style="background-color: #28a745; color: white; padding: 12px 24px; text-decoration: none; border-radius: 8px; display: inline-block; font-weight: bold;">
           Accepter l'activation
        </a>
      `
    };

    const userMailOptions = {
      from: '"administrateur" <oldvivaldi@gmail.com>',
      to: email,
      subject: "Confirmation de votre demande d'activation",
      text: `Bonjour ${login},\n\nVotre demande d'activation a bien été transmise à l'administrateur.\nVous recevrez un e-mail dès que votre compte sera prêt.\n\nCordialement,\nL'équipe de Nathanaël.`
    };

    try {
      await Promise.all([
        transporter.sendMail(adminMailOptions),
        transporter.sendMail(userMailOptions)
      ]);
    } catch (mailError) {
      return res.status(201).json({
        message: "Compte créé en attente, mais l'envoi des e-mails de notification a échoué.",
        warning: "Vérifiez la configuration SMTP (Mot de passe d'application Gmail)."
      });
    }

    res.json({ message: 'Compte créé en attente et e-mails envoyés.' });
  } catch (error) {
    console.error('Erreur API /api/activate:', error);
    res.status(500).json({ error: error.message || "Erreur lors de l'activation du compte." });
  }
});

app.get('/api/confirm-activation', async (req, res) => {
  const { login, email } = req.query;

  if (!login || !email) {
    return res.status(400).send('Paramètres de validation manquants.');
  }

  try {
    await poolConnect;
    await pool.request()
      .input('login', sql.NVarChar, login)
      .query('UPDATE [dbo].[Utilisateurs] SET MustResetPassword = 1 WHERE Username = @login');

    await sendResetEmail(login, email, 'Activation de votre compte Nathanaël - Création de mot de passe');

    // FIX: escapeHtml pour éviter l'injection HTML dans la réponse admin
    res.send(`
      <div style="font-family: sans-serif; text-align: center; margin-top: 50px;">
        <h2 style="color: #28a745;">Activation validée !</h2>
        <p>L'e-mail de création de mot de passe a été envoyé à l'utilisateur (<strong>${escapeHtml(email)}</strong>).</p>
      </div>
    `);
  } catch (error) {
    console.error('Erreur confirm-activation:', error);
    res.status(500).send("Erreur lors de l'envoi de l'e-mail de confirmation à l'utilisateur.");
  }
});

// Protégé admin
app.get('/api/users', adminMiddleware, async (req, res) => {
  try {
    await poolConnect;
    const result = await pool.request()
      .query(`
        SELECT UserID, Username, Email, Role, MustResetPassword, MotDePasseIsActive
        FROM Utilisateurs
        ORDER BY Username ASC
      `);
    res.json(result.recordset);
  } catch (error) {
    console.error('API /api/users error:', error);
    res.status(500).json({ error: 'Impossible de récupérer la liste des utilisateurs.' });
  }
});

// Protégé admin
app.post('/api/users/toggle-active', adminMiddleware, async (req, res) => {
  const { login, isActive } = req.body;

  if (!login || isActive === undefined) {
    return res.status(400).json({ error: 'Paramètres manquants.' });
  }

  try {
    await poolConnect;
    await pool.request()
      .input('login', sql.NVarChar, login)
      .input('isActive', sql.Bit, isActive ? 1 : 0)
      .query(`
        UPDATE [dbo].[Utilisateurs]
        SET MotDePasseIsActive = @isActive
        WHERE Username = @login
      `);

    res.json({ message: `Statut de ${login} mis à jour : ${isActive ? 'Activé' : 'Désactivé'}.` });
  } catch (error) {
    console.error('API /api/users/toggle-active error:', error);
    res.status(500).json({ error: 'Erreur lors de la mise à jour du statut.' });
  }
});

// Protégé admin
app.post('/api/request-reset', adminMiddleware, async (req, res) => {
  const { login } = req.body;

  if (!login) {
    return res.status(400).json({ error: 'Login requis.' });
  }

  try {
    await poolConnect;

    const result = await pool.request()
      .input('login', sql.NVarChar, login)
      .query('SELECT Email FROM Utilisateurs WHERE Username = @login');

    if (result.recordset.length === 0) {
      return res.status(404).json({ error: 'Utilisateur non trouvé.' });
    }

    const email = result.recordset[0].Email;

    await pool.request()
      .input('login', sql.NVarChar, login)
      .query('UPDATE [dbo].[Utilisateurs] SET MustResetPassword = 1 WHERE Username = @login');

    await sendResetEmail(login, email);

    res.json({ message: `Le flag a été activé et le mail envoyé à ${email}.` });
  } catch (error) {
    console.error('Erreur request-reset:', error);
    res.status(500).json({ error: 'Erreur lors de la demande de réinitialisation.' });
  }
});

// Protégé admin
app.post('/api/import-csv', adminMiddleware, async (req, res) => {
  const csvString = req.body.csv;

  if (!csvString) {
    return res.status(400).json({ error: 'Contenu CSV manquant dans le corps de la requête.' });
  }

  const lines = csvString.split('\n');
  const processedRows = [];

  const monthMap = {
    'janvier': 0, 'février': 1, 'mars': 2, 'avril': 3, 'mai': 4, 'juin': 5,
    'juillet': 6, 'août': 7, 'septembre': 8, 'octobre': 9, 'novembre': 10, 'décembre': 11
  };

  const dateRegex = /\d{1,2}\s+(janvier|février|mars|avril|mai|juin|juillet|août|septembre|octobre|novembre|décembre)\s+\d{4}/i;

  for (const line of lines) {
    const text = line.trim();
    if (!text) continue;

    const dateMatch = text.match(dateRegex);
    if (!dateMatch) continue;

    const dateString = dateMatch[0];
    const parts = text.split(dateString);
    const wordsString = parts[0].replace(/^(lundi|mardi|mercredi|jeudi|vendredi|samedi|dimanche)/i, '').trim();
    const afterDate = parts[1] || '';
    const totalMatch = afterDate.match(/\d+/);
    const totalWordsRaw = totalMatch ? totalMatch[0] : '';

    processedRows.push({ wordsString, dateString, totalWordsRaw });
  }

  if (processedRows.length === 0) {
    return res.status(400).json({ error: 'Aucune donnée valide trouvée dans le CSV.' });
  }

  try {
    await poolConnect;
    const transaction = new sql.Transaction(pool);
    await transaction.begin();

    const wordCache = new Map();

    try {
      for (const row of processedRows) {
        let motId = null;
        const words = row.wordsString
          .split(',')
          .map(w => w.trim())
          .filter(w => w.length > 0);

        if (words.length > 0) {
          for (const word of words) {
            if (!wordCache.has(word)) {
              let motResult = await transaction.request()
                .input('mot', sql.NVarChar, word)
                .query('SELECT Id FROM Mots WHERE Mot = @mot');

              if (motResult.recordset.length > 0) {
                wordCache.set(word, motResult.recordset[0].Id);
              } else {
                motResult = await transaction.request()
                  .input('mot', sql.NVarChar, word)
                  .query('INSERT INTO Mots (Mot) VALUES (@mot); SELECT SCOPE_IDENTITY() AS Id;');
                wordCache.set(word, motResult.recordset[0].Id);
              }
            }
          }
          motId = words.length === 1 ? wordCache.get(words[0]) : null;
        }

        const dateParts = row.dateString.trim().split(/\s+/);
        const hasDayName = isNaN(parseInt(dateParts[0]));
        const day = parseInt(hasDayName ? dateParts[1] : dateParts[0], 10);
        const monthStr = hasDayName ? dateParts[2] : dateParts[1];
        const year = parseInt(hasDayName ? dateParts[3] : dateParts[2], 10);
        const month = monthMap[monthStr.toLowerCase()];
        const date = new Date(year, month, day);

        const total = isNaN(parseInt(row.totalWordsRaw, 10)) ? null : parseInt(row.totalWordsRaw, 10);

        await transaction.request()
          .input('motId', sql.Int, motId)
          .input('date', sql.DateTime2, date)
          .input('total', sql.Int, total)
          .query('INSERT INTO Orthophoniste (MotId, Date, Total) VALUES (@motId, @date, @total)');
      }

      await transaction.commit();
      res.json({ message: `${processedRows.length} enregistrements CSV importés avec succès.` });
    } catch (err) {
      await transaction.rollback();
      console.error("Erreur lors de l'importation CSV (transaction):", err);
      res.status(500).json({ error: "Erreur lors de l'importation des données CSV." });
    }
  } catch (error) {
    console.error('Erreur connexion BDD pour import CSV:', error);
    res.status(500).json({ error: 'Erreur de connexion à la base de données.' });
  }
});

// Protégé auth
app.get('/api/orthophoniste', authMiddleware, async (req, res) => {
  try {
    await poolConnect;
    const result = await pool.request().query(`
      SELECT
        O.Id,
        O.Date,
        O.Total,
        O.Complet,
        O.Incomplet,
        M.Mot
      FROM Orthophoniste O
      LEFT JOIN Mots M ON O.MotId = M.Id
      ORDER BY O.Date DESC
    `);
    res.json(result.recordset);
  } catch (error) {
    console.error('API /api/orthophoniste error:', error);
    res.status(500).json({ error: 'Erreur lors de la récupération des données.' });
  }
});

// Protégé auth
app.get('/api/mots', authMiddleware, async (req, res) => {
  try {
    await poolConnect;
    const result = await pool.request().query(`
      SELECT Id, Mot
      FROM Mots
      ORDER BY Mot ASC
    `);
    res.json(result.recordset);
  } catch (error) {
    console.error('API /api/mots error:', error);
    res.status(500).json({ error: 'Erreur lors de la récupération des mots.' });
  }
});

// Tâche de fond : relance toutes les 24h (au lieu de 1h) pour éviter le spam
setInterval(async () => {
  console.log(`[${new Date().toISOString()}] Vérification des relances de mot de passe...`);
  try {
    await poolConnect;
    const result = await pool.request()
      .query('SELECT Username, Email FROM Utilisateurs WHERE MustResetPassword = 1');

    for (const user of result.recordset) {
      await sendResetEmail(user.Username, user.Email);
      console.log(`Relance envoyée à : ${user.Username}`);
    }

    console.log(`[${new Date().toISOString()}] Fin de vérification. ${result.recordset.length} mail(s) envoyé(s).`);
  } catch (err) {
    console.error('Erreur lors du job de relance automatique:', err);
  }
}, 86400000);

app.use(express.static(path.join(__dirname)));

app.get('/', (req, res) => {
  res.sendFile(path.join(__dirname, 'index.html'));
});

app.listen(port, '0.0.0.0', () => {
  console.log(`Server v${apiVersion} running on port ${port} (Public URL: ${publicHost})`);
});
