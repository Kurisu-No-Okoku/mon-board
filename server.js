const path = require('path');
const express = require('express');
const sql = require('mssql');
const nodemailer = require('nodemailer');
const bcrypt = require('bcrypt');

const app = express();
const port = process.env.PORT || 3000;
const host = '100.99.13.22';
const apiVersion = '1.7.3'; 
 
const dbConfig = {
  user: process.env.DB_USER,
  password: process.env.DB_PASSWORD,
  server: process.env.DB_SERVER || host,
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

// Middleware pour autoriser Live Server (5500) à appeler l'API (3000)
app.use((req, res, next) => {
  res.header("Access-Control-Allow-Origin", "*"); 
  res.header("Access-Control-Allow-Headers", "Origin, X-Requested-With, Content-Type, Accept");
  next();
});

app.use(express.json());

// Log de chaque requête pour debug
app.use((req, res, next) => {
  console.log(`[${new Date().toISOString()}] ${req.method} ${req.url}`);
  next();
});

// Endpoint pour vérifier la version et l'état de l'API
app.get('/api/info', (req, res) => {
  res.json({ version: apiVersion, status: 'running' });
});

// Configuration du transporteur Nodemailer
const transporter = nodemailer.createTransport({
  service: 'gmail',
  auth: {
    user: 'oldvivaldi@gmail.com',
    pass: process.env.EMAIL_PASSWORD
  }
});

// Vérification de la configuration au démarrage
transporter.verify((error, success) => {
  if (error) {
    console.error('❌ Erreur configuration SMTP (Gmail) :', error.message);
  } else {
    console.log('✅ Serveur de mail prêt à envoyer des messages');
  }
});

// Helper pour l'envoi de l'e-mail de réinitialisation/création de MDP
async function sendResetEmail(login, email, customSubject = null) {
  const userMailOptions = {
    from: '"administrateur" <oldvivaldi@gmail.com>',
    to: email,
    subject: customSubject || 'Action requise : Définissez votre mot de passe - Nathanaël',
    html: `
      <h3>Bonjour ${login},</h3>
      <p>Une action est requise sur votre compte pour définir ou réinitialiser votre mot de passe.</p>
      <p>Veuillez cliquer sur le bouton ci-dessous pour accéder à la page sécurisée :</p>
      <a href="http://${host}:${port}/reset-password.html?login=${encodeURIComponent(login)}" 
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

app.post('/api/buttons', async (req, res) => {
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
    return res.status(400).json({ error: 'Nom d\'utilisateur requis.' });
  }

  try {
    await poolConnect;
    const result = await pool.request()
      .input('username', sql.NVarChar, username.trim())
      .query('SELECT UserID, Username, Email, Role, MustResetPassword, MotDePasseIsActive, PasswordHash FROM Utilisateurs WHERE Username = @username');

    if (result.recordset.length > 0) {
      const user = result.recordset[0];
      
      if (user.MotDePasseIsActive) {
        if (!password) {
          return res.status(400).json({ error: 'Mot de passe requis.' });
        }
        
        try {
          // Sécurité : bcrypt.compare peut échouer si le hash en BDD n'est pas au bon format (ex: 'WAITING_FOR_HASH')
          const match = await bcrypt.compare(password, user.PasswordHash);
          if (!match) {
            return res.status(401).json({ error: 'Identifiant ou mot de passe incorrect.' });
          }
        } catch (bcryptError) {
          console.error('Erreur de comparaison Bcrypt (hash invalide ?):', bcryptError.message);
          return res.status(401).json({ error: 'Identifiant ou mot de passe incorrect.' });
        }
      }
      
      // Si le mot de passe n'est pas encore actif ou s'il correspond, on connecte
      res.json(user);
    } else {
      res.status(401).json({ error: 'Utilisateur non reconnu' });
    }
  } catch (error) {
    console.error('API /api/login error:', error);
    res.status(500).json({ error: 'Erreur lors de la vérification de l\'utilisateur.' });
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
    // 1. Vérification si l'utilisateur existe déjà pour éviter une erreur SQL de contrainte unique
    await poolConnect;
    const checkUser = await pool.request()
      .input('login', sql.NVarChar, login)
      .query('SELECT UserID FROM Utilisateurs WHERE Username = @login');

    if (checkUser.recordset.length > 0) {
      return res.status(409).json({ error: 'Cet identifiant est déjà utilisé ou en attente.' });
    }

    // 2. Insertion en base de données
    await pool.request()
      .input('login', sql.NVarChar, login)
      .input('email', sql.NVarChar, email)
      .query(`
        INSERT INTO [dbo].[Utilisateurs] 
          (Username, Email, PasswordHash, Role, MustResetPassword, MotDePasseIsActive, UserCreatedBy, LastModificationUserBy)
        VALUES 
          (@login, @email, 'WAITING_FOR_HASH', 'User', 0, 1, @login, @login)
      `);

    console.log(`Utilisateur ${login} inséré en base (en attente).`);

    // 3. Préparation de l'e-mail pour l'administrateur avec bouton d'acceptation
    const adminMailOptions = {
      from: 'oldvivaldi@gmail.com',
      to: 'oldvivaldi@gmail.com',
      subject: `Demande d'activation de compte : ${login}`,
      html: `
        <h3>Nouvelle demande d'activation</h3>
        <p>L'utilisateur <strong>${login}</strong> (${email}) souhaite activer son compte.</p>
        <p>Cliquez sur le bouton ci-dessous pour valider sa demande et lui envoyer le lien de création de mot de passe :</p>
        <a href="http://${host}:${port}/api/confirm-activation?login=${encodeURIComponent(login)}&email=${encodeURIComponent(email)}" 
           style="background-color: #28a745; color: white; padding: 12px 24px; text-decoration: none; border-radius: 8px; display: inline-block; font-weight: bold;">
           Accepter l'activation
        </a>
      `
    };

    // 4. Mail de confirmation pour l'utilisateur
    const userMailOptions = {
      from: '"administrateur" <oldvivaldi@gmail.com>',
      to: email,
      subject: 'Confirmation de votre demande d\'activation',
      text: `Bonjour ${login},\n\nVotre demande d'activation a bien été transmise à l'administrateur.\nVous recevrez un e-mail dès que votre compte sera prêt.\n\nCordialement,\nL'équipe de Nathanaël.`
    };

    // 5. Envoi des e-mails (Admin + Utilisateur)
    try {
      await Promise.all([
        transporter.sendMail(adminMailOptions),
        transporter.sendMail(userMailOptions)
      ]);
    } catch (mailError) {
      return res.status(201).json({ 
        message: 'Compte créé en attente, mais l\'envoi des e-mails de notification a échoué.',
        warning: 'Vérifiez la configuration SMTP (Mot de passe d\'application Gmail).' 
      });
    }

    res.json({ message: 'Compte créé en attente et e-mails envoyés.' });
  } catch (error) {
    console.error('Erreur API /api/activate:', error);
    res.status(500).json({ error: error.message || 'Erreur lors de l\'activation du compte.' });
  }
});

// Nouvel endpoint pour la validation par l'administrateur
app.get('/api/confirm-activation', async (req, res) => {
  const { login, email } = req.query;

  if (!login || !email) {
    return res.status(400).send('Paramètres de validation manquants.');
  }

  try {
    await poolConnect;
    // 1. Remise à 0 du flag MustResetPassword
    await pool.request()
      .input('login', sql.NVarChar, login)
      .query('UPDATE [dbo].[Utilisateurs] SET MustResetPassword = 1 WHERE Username = @login');

    // Envoi du mail via le helper (sujet personnalisé)
    await sendResetEmail(login, email, 'Activation de votre compte Nathanaël - Création de mot de passe');

    // Réponse affichée dans le navigateur de l'admin
    res.send(`
      <div style="font-family: sans-serif; text-align: center; margin-top: 50px;">
        <h2 style="color: #28a745;">Activation validée !</h2>
        <p>L'e-mail de création de mot de passe a été envoyé à l'utilisateur (<strong>${email}</strong>).</p>
      </div>
    `);
  } catch (error) {
    console.error('Erreur confirm-activation:', error);
    res.status(500).send('Erreur lors de l\'envoi de l\'e-mail de confirmation à l\'utilisateur.');
  }
});

// Endpoint pour lister tous les utilisateurs (Admin)
app.get('/api/users', async (req, res) => {
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

// Endpoint pour activer/désactiver un utilisateur (Admin)
app.post('/api/users/toggle-active', async (req, res) => {
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

// Endpoint pour forcer une demande de réinitialisation (Admin)
app.post('/api/request-reset', async (req, res) => {
  const { login } = req.body;

  if (!login) {
    return res.status(400).json({ error: 'Login requis.' });
  }

  try {
    await poolConnect;
    
    // 1. Récupération de l'email et vérification existence
    const result = await pool.request()
      .input('login', sql.NVarChar, login)
      .query('SELECT Email FROM Utilisateurs WHERE Username = @login');

    if (result.recordset.length === 0) {
      return res.status(404).json({ error: 'Utilisateur non trouvé.' });
    }

    const email = result.recordset[0].Email;

    // 2. Bascule du flag MustResetPassword à 1
    await pool.request()
      .input('login', sql.NVarChar, login)
      .query('UPDATE [dbo].[Utilisateurs] SET MustResetPassword = 1 WHERE Username = @login');

    // 3. Envoi immédiat du mail
    await sendResetEmail(login, email);

    res.json({ message: `Le flag a été activé et le mail envoyé à ${email}.` });
  } catch (error) {
    console.error('Erreur request-reset:', error);
    res.status(500).json({ error: 'Erreur lors de la demande de réinitialisation.' });
  }
});

// Nouvel endpoint pour l'importation CSV
app.post('/api/import-csv', async (req, res) => {
  const csvString = req.body.csv; // Le contenu CSV est attendu en tant que chaîne dans le corps de la requête

  if (!csvString) {
    return res.status(400).json({ error: 'Contenu CSV manquant dans le corps de la requête.' });
  }
  const lines = csvString.split('\n');
  const processedRows = [];

  const monthMap = {
    "janvier": 0, "février": 1, "mars": 2, "avril": 3, "mai": 4, "juin": 5,
    "juillet": 6, "août": 7, "septembre": 8, "octobre": 9, "novembre": 10, "décembre": 11
  };

  // Expression régulière pour détecter une date type "vendredi 1 mai 2026"
  const dateRegex = /\d{1,2}\s+(janvier|février|mars|avril|mai|juin|juillet|août|septembre|octobre|novembre|décembre)\s+\d{4}/i;

  for (const line of lines) {
    const text = line.trim();
    if (!text) continue;

    // On cherche la date dans la ligne entière
    const dateMatch = text.match(dateRegex);
    if (!dateMatch) continue;

    const dateString = dateMatch[0];
    const parts = text.split(dateString);
    
    // Les mots sont avant la date (on retire le jour de la semaine s'il reste)
    const wordsString = parts[0].replace(/^(lundi|mardi|mercredi|jeudi|vendredi|samedi|dimanche)/i, '').trim();
    
    // Le total est le premier nombre trouvé après la date
    const afterDate = parts[1] || "";
    const totalMatch = afterDate.match(/\d+/);
    const totalWordsRaw = totalMatch ? totalMatch[0] : "";

    processedRows.push({
      wordsString,
      dateString,
      totalWordsRaw
    });
  }

  if (processedRows.length === 0) {
    return res.status(400).json({ error: 'Aucune donnée valide trouvée dans le CSV.' });
  }

  try {
    await poolConnect;
    const transaction = new sql.Transaction(pool);
    await transaction.begin();

    const wordCache = new Map(); // To store { word: MotId }

    try {
      for (const row of processedRows) {
        let motId = null;
        const words = row.wordsString
          .split(',')
          .map(w => w.trim())
          .filter(w => w.length > 0);

        // Process words for the Mots table
        // If there's exactly one word, link to it. Otherwise, MotId in Orthophoniste will be NULL.
        // All words mentioned in the CSV should be added to the Mots table.
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
            // If there's exactly one word, use its ID for MotId in Orthophoniste
            if (words.length === 1) {
                motId = wordCache.get(words[0]);
            } else {
                motId = null; // Multiple words, so MotId for the session is NULL
            }
        }

        // Parse date
        const dateParts = row.dateString.trim().split(/\s+/); 
        // Gestion si le jour de la semaine a été inclu ou non dans le match
        const hasDayName = isNaN(parseInt(dateParts[0]));
        const day = parseInt(hasDayName ? dateParts[1] : dateParts[0], 10);
        const monthStr = hasDayName ? dateParts[2] : dateParts[1];
        const year = parseInt(hasDayName ? dateParts[3] : dateParts[2], 10);
        const month = monthMap[monthStr.toLowerCase()];
        const date = new Date(year, month, day);

        // Parse total words
        const total = isNaN(parseInt(row.totalWordsRaw, 10)) ? null : parseInt(row.totalWordsRaw, 10);

        // Insert into Orthophoniste
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
      console.error('Erreur lors de l\'importation CSV (transaction):', err);
      res.status(500).json({ error: 'Erreur lors de l\'importation des données CSV.' });
    }
  } catch (error) {
    console.error('Erreur lors de la connexion à la base de données pour l\'importation CSV:', error);
    res.status(500).json({ error: 'Erreur de connexion à la base de données.' });
  }
});

app.get('/api/orthophoniste', async (req, res) => {
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

// Tâche de fond : Vérification toutes les 1 heure (3600000 ms)
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
}, 3600000);

// Servir les fichiers statiques
app.use(express.static(path.join(__dirname)));

// S'assurer que la racine renvoie bien l'index.html
app.get('/', (req, res) => {
  res.sendFile(path.join(__dirname, 'index.html'));
});

app.listen(port, '0.0.0.0', () => {
  console.log(`Server v${apiVersion} running on http://${host}:${port}`);
});
