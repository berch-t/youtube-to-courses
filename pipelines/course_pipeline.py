#!/usr/bin/env python3
"""
Course Pipeline Module - Converts transcript to SOTA French course format.
Handles translation and restructuring for optimal presentation delivery.
"""
from __future__ import annotations

import os
import re
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Optional, Tuple

from dotenv import load_dotenv

load_dotenv()

@dataclass
class CourseConfig:
    input_path: Path
    output_path: Path
    language: str = "fr"
    style: str = "mixed"  # academic, practical, mixed
    target_duration_per_section: int = 5  # minutes
    include_exercises: bool = True
    include_glossary: bool = True


class CoursePipeline:
    def __init__(self, config: CourseConfig):
        self.config = config
        self.openai_client = None
        self._init_openai()
    
    def _init_openai(self):
        """Initialize OpenAI client"""
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OPENAI_API_KEY not set in environment.")
        
        try:
            from openai import OpenAI
            self.openai_client = OpenAI(api_key=api_key)
        except ImportError:
            raise ImportError("OpenAI package not installed. Run: pip install openai")
    
    def process(self) -> Path:
        """Main processing method that converts transcript to SOTA course"""
        print("[INFO] Starting course generation pipeline...")
        
        # 1. Parse transcript
        transcript_content = self._parse_transcript()
        
        # 2. Analyze and extract structure
        structured_content = self._analyze_content_structure(transcript_content)
        
        # 3. Translate to French
        french_content = self._translate_content(structured_content)
        
        # 4. Generate course modules
        course_modules = self._generate_course_modules(french_content)
        
        # 5. Create final course document
        final_course = self._create_final_course(course_modules)
        
        # 6. Save to file
        output_file = self._save_course(final_course)
        
        print(f"[OK] SOTA Course generated: {output_file}")
        return output_file
    
    def _parse_transcript(self) -> Dict:
        """Parse the transcript markdown file"""
        content = self.config.input_path.read_text(encoding='utf-8')
        
        # Extract chunks with timestamps
        chunk_pattern = r'## Chunk \d+ \[(\d{2}:\d{2}:\d{2}) → (\d{2}:\d{2}:\d{2})\]\s*\n\n(.*?)(?=\n## |$)'
        chunks = re.findall(chunk_pattern, content, re.DOTALL)
        
        transcript_data = {
            'title': self._extract_title_from_content(content),
            'total_duration': self._calculate_total_duration(chunks),
            'chunks': [
                {
                    'start_time': start,
                    'end_time': end,
                    'content': text.strip()
                }
                for start, end, text in chunks
            ]
        }
        
        return transcript_data
    
    def _extract_title_from_content(self, content: str) -> str:
        """Extract or generate a title from the content"""
        # Look for first meaningful sentence or concept
        lines = content.split('\n')
        for line in lines:
            if len(line.strip()) > 20 and 'Chunk' not in line and '#' not in line:
                # Use OpenAI to generate a title from the first meaningful content
                return self._generate_title_from_sample(line[:500])
        return "Cours IA Avancé"
    
    def _generate_title_from_sample(self, sample_text: str) -> str:
        """Generate course title from sample content using OpenAI"""
        prompt = f"""
        Basé sur cet extrait de transcription d'un cours, génère un titre accrocheur et professionnel en français pour le cours complet.
        Le titre doit être:
        - Précis et descriptif
        - Professionnel mais engageant
        - Maximum 8 mots
        - En français
        
        Extrait: {sample_text}
        
        Réponds seulement avec le titre, sans guillemets ni explications.
        """
        
        try:
            response = self.openai_client.chat.completions.create(
                model="gpt-4-turbo",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=50,
                temperature=0.3
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            print(f"[WARN] Title generation failed: {e}")
            return "Cours IA Avancé"
    
    def _calculate_total_duration(self, chunks: List[Tuple[str, str, str]]) -> str:
        """Calculate total duration from chunks"""
        if not chunks:
            return "00:00:00"
        
        last_end = chunks[-1][1]  # end time of last chunk
        return last_end
    
    def _analyze_content_structure(self, transcript_data: Dict) -> Dict:
        """Analyze content to identify main themes and logical structure"""
        full_content = " ".join([chunk['content'] for chunk in transcript_data['chunks']])
        
        # Use OpenAI to identify main themes and create logical structure
        analysis_prompt = f"""
        Analyse cette transcription de cours et identifie:
        1. Les thèmes principaux abordés (5-8 thèmes maximum)
        2. L'ordre logique pour un cours structuré
        3. Les concepts clés pour chaque thème
        4. Les transitions naturelles entre les thèmes
        
        Transcription: {full_content[:4000]}...
        
        Réponds au format JSON:
        {{
            "themes": [
                {{
                    "titre": "Titre du thème",
                    "concepts_cles": ["concept1", "concept2"],
                    "duree_estimee": "10 minutes"
                }}
            ],
            "progression_logique": ["theme1", "theme2", "theme3"]
        }}
        """
        
        try:
            response = self.openai_client.chat.completions.create(
                model="gpt-4-turbo",
                messages=[{"role": "user", "content": analysis_prompt}],
                max_tokens=1000,
                temperature=0.2
            )
            
            import json
            analysis = json.loads(response.choices[0].message.content)
            
            # Assign content chunks to themes
            structured_content = {
                'themes': analysis['themes'],
                'progression': analysis['progression_logique'],
                'content_mapping': self._map_content_to_themes(transcript_data, analysis['themes'])
            }
            
            return structured_content
            
        except Exception as e:
            print(f"[WARN] Content analysis failed: {e}")
            # Fallback to simple chronological structure
            return self._create_fallback_structure(transcript_data)
    
    def _map_content_to_themes(self, transcript_data: Dict, themes: List[Dict]) -> Dict:
        """Map transcript chunks to identified themes"""
        content_mapping = {}
        
        for i, theme in enumerate(themes):
            # Simple mapping: divide chunks evenly among themes
            chunks_per_theme = len(transcript_data['chunks']) // len(themes)
            start_idx = i * chunks_per_theme
            end_idx = (i + 1) * chunks_per_theme if i < len(themes) - 1 else len(transcript_data['chunks'])
            
            content_mapping[theme['titre']] = transcript_data['chunks'][start_idx:end_idx]
        
        return content_mapping
    
    def _create_fallback_structure(self, transcript_data: Dict) -> Dict:
        """Create a fallback structure when analysis fails"""
        chunks = transcript_data['chunks']
        themes_count = min(6, max(3, len(chunks) // 2))  # 3-6 themes
        
        themes = []
        for i in range(themes_count):
            themes.append({
                'titre': f"Module {i+1}",
                'concepts_cles': ["Concepts principaux", "Applications pratiques"],
                'duree_estimee': "8-10 minutes"
            })
        
        return {
            'themes': themes,
            'progression': [theme['titre'] for theme in themes],
            'content_mapping': self._map_content_to_themes(transcript_data, themes)
        }
    
    def _translate_content(self, structured_content: Dict) -> Dict:
        """Translate content to French and improve pedagogical structure"""
        print("[INFO] Translating and optimizing content...")
        
        translated_content = {
            'themes': [],
            'progression': structured_content['progression'],
            'content_mapping': {}
        }
        
        for theme in structured_content['themes']:
            # Translate theme metadata
            translated_theme = {
                'titre': theme['titre'],  # Already in French from analysis
                'concepts_cles': theme['concepts_cles'],
                'duree_estimee': theme['duree_estimee']
            }
            translated_content['themes'].append(translated_theme)
            
            # Translate and optimize content for this theme
            theme_chunks = structured_content['content_mapping'].get(theme['titre'], [])
            if theme_chunks:
                combined_content = " ".join([chunk['content'] for chunk in theme_chunks])
                optimized_content = self._translate_and_optimize_section(
                    combined_content, 
                    theme['titre'],
                    theme['concepts_cles']
                )
                translated_content['content_mapping'][theme['titre']] = optimized_content
        
        return translated_content
    
    def _translate_and_optimize_section(self, content: str, theme_title: str, key_concepts: List[str]) -> str:
        """Translate a section and optimize it for presentation with chunking support"""
        
        # Check content length and chunk if necessary (approximately 1 token = 4 characters)
        max_content_chars = 3000  # Conservative limit to stay under 8192 tokens total
        
        if len(content) <= max_content_chars:
            return self._translate_single_chunk(content, theme_title, key_concepts)
        else:
            # Split content into manageable chunks
            chunks = self._split_content_intelligently(content, max_content_chars)
            translated_chunks = []
            
            for i, chunk in enumerate(chunks):
                chunk_title = f"{theme_title} (Partie {i+1}/{len(chunks)})"
                translated_chunk = self._translate_single_chunk(chunk, chunk_title, key_concepts)
                translated_chunks.append(translated_chunk)
            
            return "\n\n".join(translated_chunks)

    def _split_content_intelligently(self, content: str, max_chars: int) -> List[str]:
        """Split content at natural breaking points (sentences, paragraphs)"""
        chunks = []
        
        # First try to split by paragraphs
        paragraphs = content.split('\n\n')
        current_chunk = ""
        
        for paragraph in paragraphs:
            if len(current_chunk) + len(paragraph) + 2 <= max_chars:
                if current_chunk:
                    current_chunk += "\n\n" + paragraph
                else:
                    current_chunk = paragraph
            else:
                # Save current chunk if not empty
                if current_chunk:
                    chunks.append(current_chunk)
                
                # If single paragraph is too long, split by sentences
                if len(paragraph) > max_chars:
                    sentence_chunks = self._split_by_sentences(paragraph, max_chars)
                    chunks.extend(sentence_chunks)
                    current_chunk = ""
                else:
                    current_chunk = paragraph
        
        # Add remaining chunk
        if current_chunk:
            chunks.append(current_chunk)
        
        return chunks

    def _split_by_sentences(self, text: str, max_chars: int) -> List[str]:
        """Split text by sentences when paragraphs are too long"""
        import re
        sentences = re.split(r'(?<=[.!?])\s+', text)
        chunks = []
        current_chunk = ""
        
        for sentence in sentences:
            if len(current_chunk) + len(sentence) + 1 <= max_chars:
                if current_chunk:
                    current_chunk += " " + sentence
                else:
                    current_chunk = sentence
            else:
                if current_chunk:
                    chunks.append(current_chunk)
                
                # If single sentence is still too long, truncate
                if len(sentence) > max_chars:
                    chunks.append(sentence[:max_chars-3] + "...")
                else:
                    current_chunk = sentence
        
        if current_chunk:
            chunks.append(current_chunk)
            
        return chunks

    def _translate_single_chunk(self, content: str, theme_title: str, key_concepts: List[str]) -> str:
        """Translate a single chunk of content"""
        prompt = f"""Tu es un expert pédagogue spécialisé dans la création de cours SOTA (State of the Art) pour des présentations live en français.

Tâche: Traduire et restructurer ce contenu de cours en français optimisé pour une présentation dynamique.

Thème: {theme_title}
Concepts clés à emphasizer: {', '.join(key_concepts)}

Contenu original: {content}

Instructions de formatting:
1. Traduis fidèlement en français académique mais accessible
2. Restructure en sections courtes (2-3 minutes chacune)
3. Utilise des listes à puces pour les points clés
4. Ajoute des questions rhétoriques pour engager l'audience
5. Inclus des transitions naturelles entre les idées
6. Marque les moments clés pour des pauses ou des démonstrations avec 🔍
7. Suggère des exemples concrets avec 💡
8. Indique les définitions importantes avec 📝

Format de réponse (markdown):
### [Titre de sous-section]

[Contenu traduit et optimisé]

🔍 **Point d'attention**: [Moment clé à emphasizer]

💡 **Exemple pratique**: [Suggestion d'exemple]

---
"""
        
        try:
            response = self.openai_client.chat.completions.create(
                model="gpt-4-turbo",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=2000,
                temperature=0.3
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            print(f"[WARN] Translation failed for {theme_title}: {e}")
            # Fallback: simple translation with chunking
            return self._simple_translate_chunked(content)
    
    def _simple_translate_chunked(self, content: str) -> str:
        """Simple translation with chunking fallback"""
        max_chunk_size = 800  # Conservative size for simple translation
        chunks = [content[i:i+max_chunk_size] for i in range(0, len(content), max_chunk_size)]
        translated_chunks = []
        
        for chunk in chunks:
            translated_chunk = self._simple_translate(chunk)
            translated_chunks.append(translated_chunk)
        
        return " ".join(translated_chunks)

    def _simple_translate(self, content: str) -> str:
        """Simple translation fallback"""
        # Truncate content to ensure we stay within token limits
        truncated_content = content[:800] if len(content) > 800 else content
        prompt = f"Traduis ce texte en français académique: {truncated_content}"
        
        try:
            response = self.openai_client.chat.completions.create(
                model="gpt-4-turbo",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=1200,
                temperature=0.2
            )
            return response.choices[0].message.content.strip()
        except Exception:
            return content  # Return original if translation fails
    
    def _generate_course_modules(self, french_content: Dict) -> List[Dict]:
        """Generate structured course modules"""
        modules = []
        
        for i, theme_title in enumerate(french_content['progression']):
            theme_data = next((t for t in french_content['themes'] if t['titre'] == theme_title), None)
            if not theme_data:
                continue
            
            content = french_content['content_mapping'].get(theme_title, "")
            
            module = {
                'numero': i + 1,
                'titre': theme_title,
                'duree_estimee': theme_data['duree_estimee'],
                'concepts_cles': theme_data['concepts_cles'],
                'contenu': content,
                'objectifs': self._generate_learning_objectives(theme_title, content),
                'questions_reflexion': self._generate_reflection_questions(theme_title, content),
                'ressources': self._generate_additional_resources(theme_title)
            }
            
            modules.append(module)
        
        return modules
    
    def _generate_learning_objectives(self, theme_title: str, content: str) -> List[str]:
        """Generate learning objectives for a module"""
        prompt = f"""
        Basé sur ce titre de module "{theme_title}" et ce contenu, génère 3-4 objectifs d'apprentissage clairs et mesurables en français.
        
        Contenu: {content[:500]}...
        
        Format: Liste de phrases commençant par des verbes d'action (comprendre, analyser, appliquer, évaluer, etc.)
        Réponds seulement avec la liste, une ligne par objectif, préfixé par "- "
        """
        
        try:
            response = self.openai_client.chat.completions.create(
                model="gpt-4-turbo",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=300,
                temperature=0.3
            )
            objectives = response.choices[0].message.content.strip().split('\n')
            return [obj.strip('- ').strip() for obj in objectives if obj.strip()]
        except Exception:
            return [f"Comprendre les concepts clés de {theme_title}",
                   f"Appliquer les principes abordés dans {theme_title}"]
    
    def _generate_reflection_questions(self, theme_title: str, content: str) -> List[str]:
        """Generate reflection questions for a module"""
        prompt = f"""
        Génère 3-4 questions de réflexion engageantes pour ce module "{theme_title}".
        Les questions doivent encourager la réflexion critique et l'application pratique.
        
        Contenu du module: {content[:500]}...
        
        Réponds seulement avec les questions, une par ligne, préfixées par "- "
        """
        
        try:
            response = self.openai_client.chat.completions.create(
                model="gpt-4-turbo",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=300,
                temperature=0.4
            )
            questions = response.choices[0].message.content.strip().split('\n')
            return [q.strip('- ').strip() for q in questions if q.strip()]
        except Exception:
            return [f"Comment pourriez-vous appliquer {theme_title} dans votre domaine ?"]
    
    def _generate_additional_resources(self, theme_title: str) -> List[str]:
        """Generate additional resources suggestions"""
        resources = [
            "Documentation officielle des frameworks mentionnés",
            "Tutoriels pratiques et exemples de code",
            "Articles de recherche récents sur le sujet",
            "Communautés et forums spécialisés"
        ]
        return resources[:2]  # Keep it concise
    
    def _create_final_course(self, modules: List[Dict]) -> str:
        """Create the final course markdown document"""
        timestamp = datetime.now().strftime("%Y-%m-%d")
        
        # Calculate total duration
        total_minutes = sum([self._parse_duration(module['duree_estimee']) for module in modules])
        total_duration = f"{total_minutes} minutes ({total_minutes//60}h{total_minutes%60:02d})"
        
        # Extract course title from first module or generate one
        course_title = self._generate_course_title([module['titre'] for module in modules])
        
        course_content = f"""# {course_title}
*Cours SOTA généré le {timestamp}*

---

## 📋 Vue d'Ensemble du Cours

### Objectifs Généraux
À la fin de ce cours, vous serez capable de :
{self._generate_global_objectives(modules)}

### 📊 Informations Pratiques
- **Durée totale estimée** : {total_duration}
- **Format** : Présentation interactive avec démonstrations
- **Niveau** : Intermédiaire à Avancé
- **Prérequis** : Connaissances de base en informatique et technologie

### 🗺️ Plan du Cours
{self._generate_course_outline(modules)}

---

"""

        # Add each module
        for module in modules:
            course_content += self._format_module(module)
        
        # Add appendices
        course_content += self._generate_appendices(modules)
        
        return course_content
    
    def _generate_course_title(self, module_titles: List[str]) -> str:
        """Generate an overarching course title"""
        prompt = f"""
        Basé sur ces titres de modules de cours, génère un titre général accrocheur et professionnel en français:
        
        Modules: {', '.join(module_titles)}
        
        Le titre doit être:
        - Maximum 8 mots
        - Professionnel mais engageant
        - Refléter le contenu global
        - En français
        
        Réponds seulement avec le titre.
        """
        
        try:
            response = self.openai_client.chat.completions.create(
                model="gpt-4-turbo",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=50,
                temperature=0.3
            )
            return response.choices[0].message.content.strip()
        except Exception:
            return "Cours d'Intelligence Artificielle Avancée"
    
    def _generate_global_objectives(self, modules: List[Dict]) -> str:
        """Generate global course objectives"""
        all_objectives = []
        for module in modules:
            all_objectives.extend(module.get('objectifs', []))
        
        # Synthesize into 4-5 global objectives
        unique_objectives = list(set(all_objectives))[:5]
        return '\n'.join([f"- {obj}" for obj in unique_objectives])
    
    def _generate_course_outline(self, modules: List[Dict]) -> str:
        """Generate course outline"""
        outline = ""
        for module in modules:
            outline += f"**Module {module['numero']}** : {module['titre']} *({module['duree_estimee']})*\n"
            key_points = module.get('concepts_cles', [])[:3]  # Top 3 key concepts
            if key_points:
                outline += f"   - {' • '.join(key_points)}\n"
            outline += "\n"
        return outline
    
    def _format_module(self, module: Dict) -> str:
        """Format a single module for the final document"""
        content = f"""## 🎯 Module {module['numero']}: {module['titre']}
*Durée estimée: {module['duree_estimee']}*

### 🎓 Objectifs d'Apprentissage
"""
        
        for objective in module.get('objectifs', []):
            content += f"- {objective}\n"
        
        content += f"""
### 📚 Contenu du Module

{module['contenu']}

### 🤔 Questions de Réflexion
"""
        
        for question in module.get('questions_reflexion', []):
            content += f"- {question}\n"
        
        if module.get('ressources'):
            content += "\n### 🔗 Ressources Complémentaires\n"
            for resource in module['ressources']:
                content += f"- {resource}\n"
        
        content += "\n---\n\n"
        return content
    
    def _generate_appendices(self, modules: List[Dict]) -> str:
        """Generate appendices (glossary, references, etc.)"""
        appendices = f"""## 📚 Annexes

### 📖 Glossaire
*Termes techniques clés utilisés dans ce cours*

{self._generate_glossary(modules)}

### 🔄 Résumé Exécutif
*Points clés à retenir de chaque module*

{self._generate_executive_summary(modules)}

### ❓ Questions Fréquemment Posées

**Q: Quels sont les prérequis techniques pour suivre ce cours ?**
A: Des connaissances de base en informatique sont recommandées, mais le cours est conçu pour être accessible.

**Q: Comment puis-je approfondir certains sujets ?**
A: Consultez les ressources complémentaires mentionnées dans chaque module et n'hésitez pas à explorer les liens fournis.

**Q: Ce cours est-il adapté aux débutants ?**
A: Ce cours vise un niveau intermédiaire, mais les concepts sont expliqués de manière progressive.

### 🎯 Prochaines Étapes Recommandées
- Pratiquer les concepts abordés à travers des projets personnels
- Rejoindre des communautés spécialisées dans le domaine
- Continuer la veille technologique sur les dernières avancées
- Partager vos apprentissages avec d'autres passionnés

---

*Cours généré par le système SOTA Course Builder - {datetime.now().strftime("%Y-%m-%d %H:%M")}*
"""
        return appendices
    
    def _generate_glossary(self, modules: List[Dict]) -> str:
        """Generate a glossary of terms"""
        # Extract technical terms from content and generate definitions
        glossary_items = [
            "**Intelligence Artificielle (IA)** : Capacité d'une machine à imiter l'intelligence humaine",
            "**Apprentissage Automatique** : Méthode permettant aux machines d'apprendre sans programmation explicite",
            "**Réseaux de Neurones** : Modèles computationnels inspirés du fonctionnement du cerveau humain",
            "**Traitement du Langage Naturel** : Branche de l'IA qui permet aux machines de comprendre le langage humain"
        ]
        
        return '\n'.join(glossary_items)
    
    def _generate_executive_summary(self, modules: List[Dict]) -> str:
        """Generate executive summary"""
        summary = ""
        for module in modules:
            key_concepts = module.get('concepts_cles', [])[:2]
            summary += f"**{module['titre']}** : {' • '.join(key_concepts)}\n"
        return summary
    
    def _parse_duration(self, duration_str: str) -> int:
        """Parse duration string to minutes"""
        # Extract numbers from strings like "8-10 minutes" or "10 minutes"
        import re
        numbers = re.findall(r'\d+', duration_str)
        if numbers:
            return int(numbers[0])  # Take first number
        return 10  # Default fallback
    
    def _save_course(self, course_content: str) -> Path:
        """Save the course to a file"""
        output_file = self.config.output_path
        output_file.parent.mkdir(parents=True, exist_ok=True)
        
        output_file.write_text(course_content, encoding='utf-8')
        return output_file


def create_course_pipeline(input_path: str, output_path: str, **kwargs) -> CoursePipeline:
    """Factory function to create CoursePipeline with sensible defaults"""
    config = CourseConfig(
        input_path=Path(input_path),
        output_path=Path(output_path),
        language=kwargs.get('language', 'fr'),
        style=kwargs.get('style', 'mixed'),
        target_duration_per_section=kwargs.get('target_duration_per_section', 5),
        include_exercises=kwargs.get('include_exercises', True),
        include_glossary=kwargs.get('include_glossary', True)
    )
    return CoursePipeline(config)