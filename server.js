const path = require('path');
const express = require('express');
const sql = require('mssql');
const nodemailer = require('nodemailer');

const app = express();
const port = process.env.PORT || 3000;
const host = '100.99.13.22';
const apiVersion = '1.2.0';

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
  const { username } = req.body;

  if (!username) {
    return res.status(400).json({ error: 'Nom d\'utilisateur requis.' });
  }

  try {
    await poolConnect;
    const result = await pool.request()
      .input('username', sql.NVarChar, username)
      .query('SELECT UserID, Username, Role, MotDePasseIsActive FROM Utilisateurs WHERE Username = @username');

    if (result.recordset.length > 0) {
      const user = result.recordset[0];
      
      // Logique sans mot de passe
      if (user.MotDePasseIsActive === true) {
        return res.status(401).json({ error: 'Mot de passe requis (non implémenté).' });
      }
      
      res.json(user);
    } else {
      res.status(401).json({ error: 'Utilisateur non reconnu' });
    }
  } catch (error) {
    console.error('API /api/login error:', error);
    res.status(500).json({ error: 'Erreur lors de la vérification de l\'utilisateur.' });
  }
});

app.post('/api/activate', async (req, res) => {
  const { login, email } = req.body;

  if (!login || !email) {
    return res.status(400).json({ error: 'Login et email requis.' });
  }

  try {
    // 1. Insertion en base de données
    await poolConnect;
    await pool.request()
      .input('login', sql.NVarChar, login)
      .input('email', sql.NVarChar, email)
      .query(`
        INSERT INTO [dbo].[Utilisateurs] 
          (Username, Email, PasswordHash, Role, MustResetPassword, MotDePasseIsActive, UserCreatedBy, LastModificationUserBy)
        VALUES 
          (@login, @email, 'WAITING_FOR_HASH', 'User', 1, 0, @login, @login)
      `);

    console.log(`Utilisateur ${login} inséré en base (en attente).`);

    // 2. Mail pour l'administrateur
    const adminMailOptions = {
      from: 'oldvivaldi@gmail.com',
      to: 'oldvivaldi@gmail.com',
      subject: `Demande d'activation de compte : ${login}`,
      text: `Bonjour,\n\nL'utilisateur "${login}" souhaite activer son compte.\nEmail de contact : ${email}\n\nCordialement.`
    };

    // 3. Mail de confirmation pour l'utilisateur
    const userMailOptions = {
      from: 'oldvivaldi@gmail.com',
      to: email,
      subject: 'Confirmation de votre demande d\'activation',
      text: `Bonjour ${login},\n\nVotre demande d'activation a bien été transmise à l'administrateur.\nVous recevrez un e-mail dès que votre compte sera prêt.\n\nCordialement,\nL'équipe de Nathanaël.`
    };

    // Envoi des e-mails
    await transporter.sendMail(adminMailOptions);
    await transporter.sendMail(userMailOptions);

    res.json({ message: 'Compte créé en attente et e-mails envoyés.' });
  } catch (error) {
    console.error('Erreur API /api/activate:', error);
    res.status(500).json({ error: 'Erreur lors de l\'envoi des e-mails.' });
  }
});

// Servir les fichiers statiques
app.use(express.static(path.join(__dirname)));

// S'assurer que la racine renvoie bien l'index.html
app.get('/', (req, res) => {
  res.sendFile(path.join(__dirname, 'index.html'));
});

app.listen(port, '0.0.0.0', () => {
  console.log(`Server v${apiVersion} running on http://${host}:${port}`);
});
