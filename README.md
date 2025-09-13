# YouTube Course Builder 🎓

Une application web moderne qui transforme automatiquement vos vidéos YouTube en cours professionnels en français, optimisés pour des présentations dynamiques et engageantes.

## ✨ Fonctionnalités

- **🎥 Mode URL YouTube** : Transcription automatique depuis une URL YouTube
- **📁 Mode Fichier Local** : Conversion de transcriptions existantes
- **🔄 Traduction Intelligente** : Conversion contextuelle en français avec OpenAI GPT-4
- **📚 Structure Pédagogique** : Réorganisation automatique en modules logiques
- **🎯 Optimisé pour le Live** : Format spécialement conçu pour les présentations
- **⚡ Interface Moderne** : UI responsive avec suivi en temps réel

## 🚀 Installation Rapide

### Prérequis
- Python 3.8+
- FFmpeg (pour le traitement audio)
- Clé API OpenAI

### 1. Cloner le projet
```bash
git clone <repository-url>
cd youtube-course-builder
```

### 2. Installer les dépendances
```bash
pip install -r requirements.txt
```

### 3. Configurer les variables d'environnement
Créez un fichier `.env` :
```env
OPENAI_API_KEY=sk-your-openai-key-here
FLASK_SECRET_KEY=your-secret-key-for-sessions
```

### 4. Installer FFmpeg

**Windows (Chocolatey)**:
```cmd
choco install ffmpeg
```

**Windows (Scoop)**:
```cmd
scoop install ffmpeg
```

**Ubuntu/Debian**:
```bash
sudo apt-get update && sudo apt-get install -y ffmpeg
```

**macOS (Homebrew)**:
```bash
brew install ffmpeg
```

### 5. Lancer l'application
```bash
python app.py
```

L'application sera accessible sur : **http://localhost:5000**

## 📖 Guide d'Utilisation

### Mode URL YouTube
1. Collez l'URL d'une vidéo YouTube
2. Sélectionnez la durée des chunks (10 min recommandé)
3. Cliquez sur "Générer le Cours SOTA"
4. Suivez le progression en temps réel
5. Téléchargez votre cours une fois terminé

### Mode Fichier Local
1. Cliquez sur "Browse" pour sélectionner votre fichier `.md`
2. Spécifiez le nom du cours de sortie
3. Cliquez sur "Convertir en Cours SOTA"
4. Téléchargez le résultat

## 📁 Structure du Projet

```
youtube-course-builder/
├── app.py                    # Application Flask principale
├── pipelines/
│   ├── audio_pipeline.py     # Pipeline de transcription audio
│   └── course_pipeline.py    # Pipeline de génération de cours
├── templates/
│   ├── base.html            # Template de base
│   ├── index.html           # Interface principale
│   ├── 404.html             # Page d'erreur 404
│   └── 500.html             # Page d'erreur 500
├── static/
│   ├── css/style.css        # Styles personnalisés
│   └── js/app.js            # JavaScript frontend
├── cache/                   # Cache des transcriptions
├── outputs/                 # Cours générés
├── uploads/                 # Fichiers uploadés
├── requirements.txt         # Dépendances Python
└── README.md               # Documentation
```

## 🛠️ Architecture Technique

### Pipelines Séparés
- **AudioPipeline** : Gère le téléchargement YouTube et la transcription Whisper
- **CoursePipeline** : Traduit et structure le contenu pour créer un cours SOTA

### Interface Flask
- Routes API RESTful
- Traitement asynchrone avec suivi des tâches
- Interface responsive moderne avec Bootstrap 5

### Fonctionnalités Avancées
- Validation d'URL YouTube en temps réel
- Drag & drop pour les fichiers
- Progress bars avec estimations de temps
- Gestion d'erreurs robuste
- Auto-génération de noms de fichiers

## 🔧 Configuration Avancée

### Variables d'Environnement
```env
# Obligatoires
OPENAI_API_KEY=sk-your-key
FLASK_SECRET_KEY=your-secret-key

# Optionnelles
FFMPEG_BINARY=/path/to/ffmpeg  # Si FFmpeg n'est pas dans PATH
```

### Personnalisation
- Modifiez `static/css/style.css` pour personnaliser l'apparence
- Ajustez les paramètres dans `pipelines/course_pipeline.py` pour la génération de cours
- Configurez les chunks audio dans `pipelines/audio_pipeline.py`

## 🚀 Déploiement Production

### Avec Gunicorn
```bash
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:8000 app:app
```

### Avec Docker (optionnel)
```dockerfile
FROM python:3.9-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
EXPOSE 5000
CMD ["python", "app.py"]
```

## ⚠️ Remarques Importantes

- **Clé OpenAI** : Nécessaire pour la traduction et la structuration
- **Limite de fichiers** : 50MB maximum pour les uploads
- **Formats supportés** : Fichiers Markdown (.md) uniquement
- **Cookies YouTube** : Placez `www.youtube.com_cookies.txt` dans le dossier pour les vidéos privées

## 🐛 Dépannage

### Erreur SSL
Si vous obtenez "No module named 'ssl'", réinstallez Python depuis python.org (version officielle).

### Erreur FFmpeg
Assurez-vous que FFmpeg est installé et accessible depuis PATH, ou définissez `FFMPEG_BINARY`.

### Erreur OpenAI
Vérifiez que votre clé API OpenAI est valide et que vous avez des crédits suffisants.

## 📄 Licence

Ce projet est sous licence MIT. Voir le fichier `LICENSE` pour plus de détails.

## 🤝 Contribution

Les contributions sont les bienvenues ! Veuillez ouvrir une issue pour discuter des changements majeurs.

## 📞 Support

Pour toute question ou problème, ouvrez une issue sur GitHub ou contactez l'équipe de développement.

---

**Fait avec ❤️ pour la communauté éducative francophone**