#!/usr/bin/env python3
"""
SOTA Course Pipeline - Advanced wrapper around existing course_pipeline.py
Preserves 100% backward compatibility while adding SOTA features as optional extensions.
"""
from __future__ import annotations

import os
import json
import requests
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Optional, Any
from enum import Enum

from .course_pipeline import CoursePipeline, CourseConfig, create_course_pipeline

class DifficultyLevel(Enum):
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"
    EXPERT = "expert"

class PedagogicalFramework(Enum):
    STANDARD = "standard"
    BLOOMS_TAXONOMY = "blooms_taxonomy"
    CONSTRUCTIVIST = "constructivist"
    COMPETENCY_BASED = "competency_based"

class CitationStyle(Enum):
    BASIC = "basic"
    ACADEMIC = "academic"
    DOCTORAL = "doctoral"
    IEEE = "ieee"
    APA = "apa"

class ProcessingMode(Enum):
    FAST = "fast"
    QUALITY = "quality"
    SOTA = "sota"

@dataclass
class SOTAOptions:
    """Configuration options for SOTA features - all optional and backward compatible"""
    
    # Core SOTA toggles
    enable_sota: bool = False
    research_integration: bool = False
    academic_citations: bool = False
    advanced_templates: bool = False
    quality_enhancement: bool = False
    
    # Content customization
    difficulty_level: DifficultyLevel = DifficultyLevel.INTERMEDIATE
    pedagogical_framework: PedagogicalFramework = PedagogicalFramework.STANDARD
    citation_style: CitationStyle = CitationStyle.BASIC
    processing_mode: ProcessingMode = ProcessingMode.QUALITY
    
    # Advanced options
    language_sophistication: str = "technique"  # simple, technique, academique
    include_math_formulas: bool = False
    include_code_examples: bool = True
    include_visual_suggestions: bool = False
    target_audience: str = "general"  # students, professionals, researchers
    
    # Research options
    arxiv_search_enabled: bool = False
    papers_with_code_integration: bool = False
    recent_papers_only: bool = True  # 2023-2025
    max_references: int = 10
    
    # Quality assurance
    fact_checking: bool = False
    readability_optimization: bool = False
    consistency_validation: bool = False
    
    # Template options
    template_style: str = "modern"  # classic, modern, academic
    include_prerequisites: bool = True
    include_exercises: bool = True
    include_assessments: bool = False
    
    # Output customization
    generate_slides_suggestions: bool = False
    include_timing_estimates: bool = True
    add_interaction_points: bool = False


class SOTACoursePipeline(CoursePipeline):
    """
    SOTA Course Pipeline - Extends existing CoursePipeline without breaking compatibility.
    
    When sota_options.enable_sota = False: Behaves exactly like original CoursePipeline
    When sota_options.enable_sota = True: Adds SOTA features as extensions
    """
    
    def __init__(self, config: CourseConfig, sota_options: Optional[SOTAOptions] = None):
        # Initialize parent class (preserves all original functionality)
        super().__init__(config)
        
        # SOTA extensions (optional)
        self.sota_options = sota_options or SOTAOptions()
        
        # Initialize SOTA modules only if needed
        self.research_engine = None
        self.citation_manager = None
        self.template_enforcer = None
        self.quality_assessor = None
        
        if self.sota_options.enable_sota:
            self._initialize_sota_modules()
    
    def _initialize_sota_modules(self):
        """Initialize SOTA modules only when needed"""
        try:
            if self.sota_options.research_integration:
                from .research_engine import ResearchEngine
                self.research_engine = ResearchEngine(self.sota_options)
                
            if self.sota_options.academic_citations:
                from .citation_manager import CitationManager
                self.citation_manager = CitationManager(self.sota_options)
                
            if self.sota_options.advanced_templates:
                from .template_enforcer import TemplateEnforcer
                self.template_enforcer = TemplateEnforcer(self.sota_options)
                
            if self.sota_options.quality_enhancement:
                from .quality_assessor import QualityAssessor
                self.quality_assessor = QualityAssessor(self.sota_options)
                
        except ImportError as e:
            print(f"[WARN] SOTA module not available: {e}. Falling back to standard mode.")
            self.sota_options.enable_sota = False
    
    def process(self) -> Path:
        """
        Main processing method - backward compatible.
        
        If SOTA disabled: Uses original pipeline exactly
        If SOTA enabled: Adds extensions while preserving core functionality
        """
        if not self.sota_options.enable_sota:
            # Pure backward compatibility - original pipeline unchanged
            return super().process()
        else:
            # SOTA enhanced processing
            return self._process_sota()
    
    def _process_sota(self) -> Path:
        """SOTA enhanced processing workflow"""
        print("[INFO] Starting SOTA Course Generation Pipeline...")
        
        # Stage 1: Enhanced content parsing (with original as base)
        transcript_content = self._parse_transcript()
        
        # Stage 2: Research integration (SOTA addition)
        if self.sota_options.research_integration and self.research_engine:
            transcript_content = self.research_engine.enhance_with_research(transcript_content)
        
        # Stage 3: Advanced content analysis (enhanced version of original)
        structured_content = self._analyze_content_structure_sota(transcript_content)
        
        # Stage 4: Enhanced translation with pedagogical frameworks
        french_content = self._translate_content_sota(structured_content)
        
        # Stage 5: SOTA module generation
        course_modules = self._generate_course_modules_sota(french_content)
        
        # Stage 6: Advanced template application
        if self.sota_options.advanced_templates and self.template_enforcer:
            final_course = self.template_enforcer.apply_sota_template(course_modules)
        else:
            final_course = self._create_final_course_sota(course_modules)
        
        # Stage 7: Quality enhancement
        if self.sota_options.quality_enhancement and self.quality_assessor:
            final_course = self.quality_assessor.enhance_quality(final_course)
        
        # Stage 8: Citation integration
        if self.sota_options.academic_citations and self.citation_manager:
            final_course = self.citation_manager.integrate_citations(final_course)
        
        # Stage 9: Save enhanced course
        output_file = self._save_course(final_course)
        
        print(f"[OK] SOTA Course generated: {output_file}")
        return output_file
    
    def _analyze_content_structure_sota(self, transcript_data: Dict) -> Dict:
        """Enhanced content analysis with SOTA features"""
        # Start with original analysis
        structured_content = super()._analyze_content_structure(transcript_data)
        
        if not self.sota_options.enable_sota:
            return structured_content
        
        # SOTA enhancements
        full_content = " ".join([chunk['content'] for chunk in transcript_data['chunks']])
        
        # Enhanced analysis prompt based on pedagogical framework
        framework_instructions = self._get_framework_instructions()
        difficulty_instructions = self._get_difficulty_instructions()
        
        enhanced_prompt = f"""
        {framework_instructions}
        
        {difficulty_instructions}
        
        Analyse cette transcription selon les critères SOTA suivants:
        1. Identifie 5-8 modules pédagogiques optimaux
        2. Structure selon {self.sota_options.pedagogical_framework.value}
        3. Calibre pour niveau {self.sota_options.difficulty_level.value}
        4. Intègre des objectifs d'apprentissage mesurables
        5. Suggère des évaluations adaptées
        
        Transcription: {full_content[:6000]}...
        
        Réponds au format JSON enrichi:
        {{
            "pedagogical_framework": "{self.sota_options.pedagogical_framework.value}",
            "difficulty_level": "{self.sota_options.difficulty_level.value}",
            "target_audience": "{self.sota_options.target_audience}",
            "themes": [
                {{
                    "titre": "Titre du module",
                    "concepts_cles": ["concept1", "concept2"],
                    "duree_estimee": "X minutes",
                    "difficulte": 1-5,
                    "objectifs_bloom": ["comprendre", "analyser", "appliquer"],
                    "prerequis": ["prerequis1", "prerequis2"],
                    "evaluations": ["type d'évaluation suggérée"]
                }}
            ],
            "progression_logique": ["module1", "module2"],
            "competences_transversales": ["competence1", "competence2"],
            "liens_conceptuels": [["module1", "module2", "relation"]]
        }}
        """
        
        try:
            response = self.openai_client.chat.completions.create(
                model="gpt-4",
                messages=[{"role": "user", "content": enhanced_prompt}],
                max_tokens=2000,
                temperature=0.1  # Lower temperature for more structured output
            )
            
            import json
            sota_analysis = json.loads(response.choices[0].message.content)
            
            # Merge SOTA analysis with original structure
            structured_content.update(sota_analysis)
            structured_content['content_mapping'] = self._map_content_to_themes(
                transcript_data, 
                sota_analysis.get('themes', structured_content.get('themes', []))
            )
            
            return structured_content
            
        except Exception as e:
            print(f"[WARN] SOTA content analysis failed: {e}. Using enhanced fallback.")
            return self._create_enhanced_fallback_structure(transcript_data, structured_content)
    
    def _get_framework_instructions(self) -> str:
        """Get pedagogical framework specific instructions"""
        frameworks = {
            PedagogicalFramework.BLOOMS_TAXONOMY: """
            Structure selon la taxonomie de Bloom:
            - Niveau 1: Mémoriser (définitions, termes)
            - Niveau 2: Comprendre (concepts, principes)
            - Niveau 3: Appliquer (problèmes, exercices)
            - Niveau 4: Analyser (comparaisons, décomposition)
            - Niveau 5: Évaluer (critiques, jugements)
            - Niveau 6: Créer (synthèse, innovation)
            """,
            PedagogicalFramework.CONSTRUCTIVIST: """
            Approche constructiviste:
            - Partir des connaissances préalables
            - Construire progressivement les concepts
            - Favoriser l'apprentissage par découverte
            - Intégrer des expériences pratiques
            - Encourager la réflexion métacognitive
            """,
            PedagogicalFramework.COMPETENCY_BASED: """
            Approche par compétences:
            - Définir des compétences observables et mesurables
            - Structurer par situations d'apprentissage
            - Intégrer théorie et pratique
            - Évaluer par performance authentique
            - Permettre différents parcours d'apprentissage
            """
        }
        
        return frameworks.get(self.sota_options.pedagogical_framework, "")
    
    def _get_difficulty_instructions(self) -> str:
        """Get difficulty level specific instructions"""
        levels = {
            DifficultyLevel.BEGINNER: """
            Niveau débutant:
            - Concepts fondamentaux uniquement
            - Vocabulaire simplifié
            - Exemples concrets et familiers
            - Progression très graduelle
            - Révisions fréquentes
            """,
            DifficultyLevel.INTERMEDIATE: """
            Niveau intermédiaire:
            - Concepts avancés avec prérequis
            - Terminologie technique appropriée
            - Exemples variés et applications
            - Connexions entre concepts
            - Défis modérés
            """,
            DifficultyLevel.ADVANCED: """
            Niveau avancé:
            - Concepts complexes et abstraits
            - Terminologie spécialisée
            - Cas d'usage sophistiqués
            - Analyse critique requise
            - Défis intellectuels élevés
            """,
            DifficultyLevel.EXPERT: """
            Niveau expert:
            - État de l'art et recherche actuelle
            - Terminologie académique précise
            - Études de cas complexes
            - Contributions originales attendues
            - Défis de niveau recherche
            """
        }
        
        return levels.get(self.sota_options.difficulty_level, "")
    
    def _translate_content_sota(self, structured_content: Dict) -> Dict:
        """Enhanced translation with SOTA pedagogical improvements"""
        if not self.sota_options.enable_sota:
            return super()._translate_content(structured_content)
        
        print("[INFO] SOTA translation and pedagogical optimization...")
        
        translated_content = {
            'themes': [],
            'progression': structured_content['progression'],
            'content_mapping': {},
            'pedagogical_metadata': structured_content.get('pedagogical_framework', {}),
            'difficulty_metadata': structured_content.get('difficulty_level', {}),
            'competences_transversales': structured_content.get('competences_transversales', [])
        }
        
        for theme in structured_content['themes']:
            # Enhanced theme processing
            translated_theme = self._process_theme_sota(theme, structured_content)
            translated_content['themes'].append(translated_theme)
            
            # Enhanced content translation
            theme_chunks = structured_content['content_mapping'].get(theme['titre'], [])
            if theme_chunks:
                combined_content = " ".join([chunk['content'] for chunk in theme_chunks])
                optimized_content = self._translate_and_optimize_section_sota(
                    combined_content, 
                    translated_theme,
                    structured_content
                )
                translated_content['content_mapping'][translated_theme['titre']] = optimized_content
        
        return translated_content
    
    def _process_theme_sota(self, theme: Dict, structured_content: Dict) -> Dict:
        """Process theme with SOTA enhancements"""
        enhanced_theme = {
            'titre': theme['titre'],
            'concepts_cles': theme.get('concepts_cles', []),
            'duree_estimee': theme.get('duree_estimee', '10 minutes'),
            'difficulte': theme.get('difficulte', 3),
            'objectifs_bloom': theme.get('objectifs_bloom', []),
            'prerequis': theme.get('prerequis', []),
            'evaluations': theme.get('evaluations', []),
            'competences_visees': [],
            'mots_cles_techniques': [],
            'suggestions_visuelles': []
        }
        
        # Add SOTA enhancements based on options
        if self.sota_options.include_visual_suggestions:
            enhanced_theme['suggestions_visuelles'] = self._generate_visual_suggestions(theme['titre'])
        
        if self.sota_options.pedagogical_framework == PedagogicalFramework.BLOOMS_TAXONOMY:
            enhanced_theme['taxonomie_bloom'] = self._map_to_bloom_levels(theme)
        
        return enhanced_theme
    
    def _translate_and_optimize_section_sota(self, content: str, theme: Dict, context: Dict) -> str:
        """SOTA enhanced section translation and optimization"""
        
        # Build sophisticated prompt based on SOTA options
        sota_instructions = self._build_sota_translation_instructions(theme, context)
        
        prompt = f"""
        Tu es un expert pédagogue de niveau doctoral, spécialiste en IA/ML/DL et en ingénierie pédagogique avancée.

        {sota_instructions}

        Contexte pédagogique:
        - Framework: {self.sota_options.pedagogical_framework.value}
        - Niveau: {self.sota_options.difficulty_level.value}
        - Audience: {self.sota_options.target_audience}
        - Style: {self.sota_options.language_sophistication}

        Thème: {theme['titre']}
        Concepts clés: {', '.join(theme.get('concepts_cles', []))}
        Objectifs Bloom: {', '.join(theme.get('objectifs_bloom', []))}

        Contenu original: {content}

        Instructions SOTA:
        1. Traduis en français {self.sota_options.language_sophistication}
        2. Structure selon {self.sota_options.pedagogical_framework.value}
        3. Adapte au niveau {self.sota_options.difficulty_level.value}
        4. Intègre les objectifs pédagogiques spécifiés
        5. Ajoute des liens vers des concepts connexes
        6. Suggère des moments d'interaction avec 🤝
        7. Indique les points d'évaluation avec 📊
        8. Marque les concepts clés avec 🔑
        9. Suggère des démonstrations avec 🔬
        10. Ajoute des références temporaires avec [REF-XX]

        Format de réponse SOTA (markdown):
        ### 🎯 {theme['titre']} 
        
        **⏱️ Durée**: {theme.get('duree_estimee', 'X minutes')} | **📊 Difficulté**: {theme.get('difficulte', 'X')}/5

        #### 📚 Prérequis Activés
        - [Liste des prérequis nécessaires]

        #### 🎓 Objectifs Pédagogiques
        - [Objectifs selon framework choisi]

        #### 📖 Contenu Principal
        [Contenu traduit et structuré avec marqueurs pédagogiques]

        🔑 **Concept Clé**: [Définition précise]
        
        🤝 **Moment d'Interaction**: [Suggestion d'activité]
        
        🔬 **Démonstration**: [Suggestion de démonstration]

        📊 **Point d'Évaluation**: [Question ou exercice]

        #### 🔗 Liens Conceptuels
        - [Connexions avec autres modules]

        #### 📚 Références Suggérées
        - [REF-01]: [Description de la référence nécessaire]

        ---
        """
        
        try:
            response = self.openai_client.chat.completions.create(
                model="gpt-4",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=3000,
                temperature=0.2
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            print(f"[WARN] SOTA translation failed for {theme['titre']}: {e}")
            # Fallback to original translation method
            return super()._translate_and_optimize_section(
                content, 
                theme['titre'], 
                theme.get('concepts_cles', [])
            )
    
    def _build_sota_translation_instructions(self, theme: Dict, context: Dict) -> str:
        """Build specific instructions based on SOTA options"""
        instructions = []
        
        if self.sota_options.include_math_formulas:
            instructions.append("- Inclus les formules mathématiques pertinentes en LaTeX")
        
        if self.sota_options.include_code_examples:
            instructions.append("- Ajoute des exemples de code pratiques et commentés")
        
        if self.sota_options.include_visual_suggestions:
            instructions.append("- Suggère des éléments visuels (graphiques, diagrammes, animations)")
        
        if self.sota_options.target_audience == "researchers":
            instructions.append("- Adopte un ton académique avec terminologie de recherche")
        elif self.sota_options.target_audience == "students":
            instructions.append("- Adopte un ton pédagogique avec explications détaillées")
        elif self.sota_options.target_audience == "professionals":
            instructions.append("- Focus sur applications pratiques et cas d'usage industriels")
        
        return "\n".join(instructions)
    
    def _generate_course_modules_sota(self, french_content: Dict) -> List[Dict]:
        """Generate SOTA enhanced course modules"""
        if not self.sota_options.enable_sota:
            return super()._generate_course_modules(french_content)
        
        modules = []
        
        for i, theme_title in enumerate(french_content['progression']):
            theme_data = next((t for t in french_content['themes'] if t['titre'] == theme_title), None)
            if not theme_data:
                continue
            
            content = french_content['content_mapping'].get(theme_title, "")
            
            # Enhanced module with SOTA features
            module = {
                'numero': i + 1,
                'titre': theme_title,
                'duree_estimee': theme_data['duree_estimee'],
                'difficulte': theme_data.get('difficulte', 3),
                'concepts_cles': theme_data['concepts_cles'],
                'contenu': content,
                'objectifs': self._generate_learning_objectives_sota(theme_title, content, theme_data),
                'questions_reflexion': self._generate_reflection_questions_sota(theme_title, content, theme_data),
                'ressources': self._generate_additional_resources_sota(theme_title),
                'prerequis': theme_data.get('prerequis', []),
                'evaluations': theme_data.get('evaluations', []),
                'objectifs_bloom': theme_data.get('objectifs_bloom', []),
                'competences_visees': theme_data.get('competences_visees', []),
                'suggestions_visuelles': theme_data.get('suggestions_visuelles', []),
                'timing_breakdown': self._generate_timing_breakdown(theme_data),
                'interaction_points': self._extract_interaction_points(content),
                'references_needed': self._extract_references_needed(content)
            }
            
            modules.append(module)
        
        return modules
    
    def _generate_learning_objectives_sota(self, theme_title: str, content: str, theme_data: Dict) -> List[str]:
        """Generate SOTA learning objectives based on pedagogical framework"""
        framework = self.sota_options.pedagogical_framework
        difficulty = self.sota_options.difficulty_level
        
        framework_prompts = {
            PedagogicalFramework.BLOOMS_TAXONOMY: f"""
            Génère 4-5 objectifs d'apprentissage selon la taxonomie de Bloom pour le niveau {difficulty.value}.
            Utilise des verbes d'action appropriés pour chaque niveau cognitif:
            - Mémoriser: définir, lister, identifier
            - Comprendre: expliquer, décrire, interpréter  
            - Appliquer: utiliser, démontrer, calculer
            - Analyser: comparer, contraster, décomposer
            - Évaluer: critiquer, justifier, évaluer
            - Créer: concevoir, construire, proposer
            """,
            PedagogicalFramework.COMPETENCY_BASED: f"""
            Génère 3-4 compétences observables et mesurables.
            Format: "L'apprenant sera capable de [action mesurable] [critère de performance]"
            Niveau {difficulty.value}
            """,
            PedagogicalFramework.CONSTRUCTIVIST: f"""
            Génère 3-4 objectifs d'apprentissage constructivistes.
            Focus sur la construction active des connaissances et la résolution de problèmes.
            Niveau {difficulty.value}
            """
        }
        
        prompt = f"""
        {framework_prompts.get(framework, 'Génère 3-4 objectifs d'apprentissage clairs et mesurables.')}
        
        Thème: {theme_title}
        Contenu: {content[:800]}...
        Concepts clés: {', '.join(theme_data.get('concepts_cles', []))}
        
        Réponds avec une liste, une ligne par objectif, préfixé par "- "
        """
        
        try:
            response = self.openai_client.chat.completions.create(
                model="gpt-4",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=400,
                temperature=0.2
            )
            objectives = response.choices[0].message.content.strip().split('\n')
            return [obj.strip('- ').strip() for obj in objectives if obj.strip()]
        except Exception:
            # Fallback to original method
            return super()._generate_learning_objectives(theme_title, content)
    
    def _create_final_course_sota(self, modules: List[Dict]) -> str:
        """Create final SOTA course document with enhanced template"""
        if not self.sota_options.enable_sota:
            return super()._create_final_course(modules)
        
        timestamp = datetime.now().strftime("%Y-%m-%d")
        
        # Calculate enhanced metadata
        total_minutes = sum([self._parse_duration(module['duree_estimee']) for module in modules])
        total_duration = f"{total_minutes} minutes ({total_minutes//60}h{total_minutes%60:02d})"
        average_difficulty = sum([module.get('difficulte', 3) for module in modules]) / len(modules)
        
        # Generate SOTA course title
        course_title = self._generate_course_title_sota([module['titre'] for module in modules])
        
        # SOTA template
        course_content = f"""# {course_title}
*Cours SOTA généré le {timestamp} | Niveau {self.sota_options.difficulty_level.value.title()}*

---

## 📋 Vue d'Ensemble SOTA

### 🎯 Métadonnées du Cours
- **🎓 Framework Pédagogique**: {self.sota_options.pedagogical_framework.value.replace('_', ' ').title()}
- **📊 Niveau de Difficulté**: {average_difficulty:.1f}/5 ({self.sota_options.difficulty_level.value.title()})
- **👥 Audience Cible**: {self.sota_options.target_audience.title()}
- **🕒 Durée Totale**: {total_duration}
- **📚 Style**: {self.sota_options.language_sophistication.title()}
- **🔬 Mode de Traitement**: {self.sota_options.processing_mode.value.upper()}

### 🎯 Objectifs Généraux du Cours
À l'issue de cette formation, vous serez capable de :
{self._generate_global_objectives_sota(modules)}

### 📊 Informations Pratiques
- **Format** : Présentation interactive avec démonstrations
- **Prérequis** : {self._compile_global_prerequisites(modules)}
- **Évaluations** : {self._compile_evaluation_methods(modules)}
- **Support** : Slides, exercices pratiques, références académiques

### 🗺️ Plan Détaillé du Cours
{self._generate_course_outline_sota(modules)}

### 🎯 Compétences Transversales Développées
{self._compile_transversal_competencies(modules)}

---

"""

        # Add each module with SOTA formatting
        for module in modules:
            course_content += self._format_module_sota(module)
        
        # Add SOTA appendices
        course_content += self._generate_appendices_sota(modules)
        
        return course_content
    
    def _create_enhanced_fallback_structure(self, transcript_data: Dict, original_structure: Dict) -> Dict:
        """Enhanced fallback when SOTA analysis fails"""
        enhanced_structure = original_structure.copy()
        
        # Add SOTA metadata to fallback
        for theme in enhanced_structure.get('themes', []):
            theme['difficulte'] = 3  # Default difficulty
            theme['objectifs_bloom'] = ['comprendre', 'appliquer']
            theme['prerequis'] = []
            theme['evaluations'] = ['Questions de révision']
        
        enhanced_structure['pedagogical_framework'] = self.sota_options.pedagogical_framework.value
        enhanced_structure['difficulty_level'] = self.sota_options.difficulty_level.value
        
        return enhanced_structure
    
    # Additional SOTA helper methods would be implemented here...
    # (For brevity, showing structure - full implementation would continue)


# Factory function for SOTA pipeline
def create_sota_course_pipeline(input_path: str, output_path: str, sota_options: Optional[SOTAOptions] = None, **kwargs) -> SOTACoursePipeline:
    """Factory function to create SOTACoursePipeline with backward compatibility"""
    
    # Create base config (preserves original functionality)
    config = CourseConfig(
        input_path=Path(input_path),
        output_path=Path(output_path),
        language=kwargs.get('language', 'fr'),
        style=kwargs.get('style', 'mixed'),
        target_duration_per_section=kwargs.get('target_duration_per_section', 5),
        include_exercises=kwargs.get('include_exercises', True),
        include_glossary=kwargs.get('include_glossary', True)
    )
    
    # Add SOTA options if provided
    if sota_options is None:
        sota_options = SOTAOptions()  # Default: SOTA disabled for full backward compatibility
    
    return SOTACoursePipeline(config, sota_options)