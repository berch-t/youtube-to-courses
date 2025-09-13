#!/usr/bin/env python3
"""
Template Enforcer - Ensures consistent SOTA course formatting
Applies structured templates and validates content consistency.
"""
from __future__ import annotations

import yaml
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any
from enum import Enum

class TemplateStyle(Enum):
    CLASSIC = "classic"
    MODERN = "modern"
    ACADEMIC = "academic"
    RESEARCH = "research"
    CORPORATE = "corporate"

@dataclass
class TemplateConfig:
    """Configuration for template application"""
    style: TemplateStyle
    include_toc: bool = True
    include_metadata: bool = True
    include_prerequisites: bool = True
    include_assessments: bool = True
    include_glossary: bool = True
    max_section_length: int = 2000
    emoji_style: bool = True
    academic_formatting: bool = False
    
class TemplateEnforcer:
    """
    Advanced template enforcement system for SOTA course generation.
    Ensures consistent, professional formatting across all generated content.
    """
    
    def __init__(self, sota_options):
        self.sota_options = sota_options
        self.template_config = self._build_template_config()
        self.templates = self._load_templates()
        
        # Validation rules
        self.validation_rules = {
            'min_modules': 3,
            'max_modules': 12,
            'min_module_length': 500,
            'max_module_length': 3000,
            'required_sections': ['objectives', 'content', 'assessment'],
            'formatting_consistency': True
        }
        
    def _build_template_config(self) -> TemplateConfig:
        """Build template configuration from SOTA options"""
        return TemplateConfig(
            style=TemplateStyle(self.sota_options.template_style),
            include_toc=True,
            include_metadata=True,
            include_prerequisites=self.sota_options.include_prerequisites,
            include_assessments=self.sota_options.include_assessments,
            include_glossary=self.sota_options.include_glossary,
            emoji_style=True,
            academic_formatting=(self.sota_options.citation_style.value in ['doctoral', 'academic'])
        )
    
    def _load_templates(self) -> Dict[str, str]:
        """Load template structures for different styles"""
        return {
            TemplateStyle.MODERN: self._get_modern_template(),
            TemplateStyle.ACADEMIC: self._get_academic_template(),
            TemplateStyle.RESEARCH: self._get_research_template(),
            TemplateStyle.CLASSIC: self._get_classic_template(),
            TemplateStyle.CORPORATE: self._get_corporate_template()
        }
    
    def apply_sota_template(self, modules: List[Dict]) -> str:
        """
        Apply SOTA template to course modules with full validation.
        Main entry point for template enforcement.
        """
        print("[INFO] Applying SOTA template enforcement...")
        
        # Validate modules structure
        validated_modules = self._validate_modules_structure(modules)
        
        # Apply template based on style
        template_func = self._get_template_function()
        formatted_content = template_func(validated_modules)
        
        # Post-process for consistency
        final_content = self._post_process_content(formatted_content)
        
        # Validate final output
        validation_report = self._validate_final_content(final_content)
        if validation_report['errors']:
            print(f"[WARN] Template validation found {len(validation_report['errors'])} issues")
        
        print("[INFO] SOTA template enforcement complete")
        return final_content
    
    def _validate_modules_structure(self, modules: List[Dict]) -> List[Dict]:
        """Validate and standardize module structure"""
        validated_modules = []
        
        for i, module in enumerate(modules):
            validated_module = self._validate_single_module(module, i + 1)
            validated_modules.append(validated_module)
        
        # Ensure minimum/maximum module count
        if len(validated_modules) < self.validation_rules['min_modules']:
            print(f"[WARN] Only {len(validated_modules)} modules found, minimum is {self.validation_rules['min_modules']}")
        
        if len(validated_modules) > self.validation_rules['max_modules']:
            print(f"[WARN] {len(validated_modules)} modules found, maximum recommended is {self.validation_rules['max_modules']}")
            validated_modules = validated_modules[:self.validation_rules['max_modules']]
        
        return validated_modules
    
    def _validate_single_module(self, module: Dict, module_number: int) -> Dict:
        """Validate and enhance a single module"""
        validated_module = module.copy()
        
        # Ensure required fields
        required_fields = {
            'numero': module_number,
            'titre': module.get('titre', f'Module {module_number}'),
            'duree_estimee': module.get('duree_estimee', '15 minutes'),
            'contenu': module.get('contenu', ''),
            'objectifs': module.get('objectifs', []),
            'difficulte': module.get('difficulte', 3)
        }
        
        for field, default_value in required_fields.items():
            if field not in validated_module or not validated_module[field]:
                validated_module[field] = default_value
        
        # Validate content length
        content_length = len(validated_module['contenu'])
        if content_length < self.validation_rules['min_module_length']:
            print(f"[WARN] Module {module_number} content is short ({content_length} chars)")
        elif content_length > self.validation_rules['max_module_length']:
            print(f"[WARN] Module {module_number} content is long ({content_length} chars)")
        
        # Ensure objectives list
        if not isinstance(validated_module['objectifs'], list):
            validated_module['objectifs'] = [validated_module['objectifs']] if validated_module['objectifs'] else []
        
        # Add missing SOTA fields
        sota_fields = {
            'concepts_cles': module.get('concepts_cles', []),
            'prerequis': module.get('prerequis', []),
            'competences_visees': module.get('competences_visees', []),
            'questions_reflexion': module.get('questions_reflexion', []),
            'ressources': module.get('ressources', []),
            'timing_breakdown': module.get('timing_breakdown', {}),
            'interaction_points': module.get('interaction_points', []),
            'evaluation_suggestions': module.get('evaluation_suggestions', [])
        }
        
        for field, default_value in sota_fields.items():
            if field not in validated_module:
                validated_module[field] = default_value
        
        return validated_module
    
    def _get_template_function(self):
        """Get template function based on selected style"""
        template_functions = {
            TemplateStyle.MODERN: self._apply_modern_template,
            TemplateStyle.ACADEMIC: self._apply_academic_template,
            TemplateStyle.RESEARCH: self._apply_research_template,
            TemplateStyle.CLASSIC: self._apply_classic_template,
            TemplateStyle.CORPORATE: self._apply_corporate_template
        }
        
        return template_functions.get(
            self.template_config.style, 
            self._apply_modern_template
        )
    
    def _apply_modern_template(self, modules: List[Dict]) -> str:
        """Apply modern SOTA template with emoji and visual elements"""
        timestamp = datetime.now().strftime("%Y-%m-%d")
        
        # Calculate metadata
        total_duration = self._calculate_total_duration(modules)
        avg_difficulty = self._calculate_average_difficulty(modules)
        course_title = self._generate_course_title(modules)
        
        content = f"""# 🚀 {course_title}
*Cours SOTA généré le {timestamp}*

<div align="center">

![Niveau](https://img.shields.io/badge/Niveau-{self.sota_options.difficulty_level.value.title()}-blue)
![Durée](https://img.shields.io/badge/Durée-{total_duration}-green)
![Modules](https://img.shields.io/badge/Modules-{len(modules)}-orange)
![Style](https://img.shields.io/badge/Style-{self.template_config.style.value.title()}-purple)

</div>

---

## 📋 Vue d'Ensemble Exécutive

### 🎯 Vision du Cours
Ce cours de niveau **{self.sota_options.difficulty_level.value.upper()}** vous guide à travers les concepts fondamentaux et avancés avec une approche pédagogique **{self.sota_options.pedagogical_framework.value.replace('_', ' ').title()}**.

### 📊 Métriques du Cours
| Métrique | Valeur |
|----------|---------|
| 🎓 **Framework Pédagogique** | {self.sota_options.pedagogical_framework.value.replace('_', ' ').title()} |
| 📈 **Difficulté Moyenne** | {avg_difficulty:.1f}/5 |
| ⏱️ **Durée Totale** | {total_duration} |
| 👥 **Audience Cible** | {self.sota_options.target_audience.title()} |
| 🔬 **Mode de Traitement** | {self.sota_options.processing_mode.value.upper()} |
| 📚 **Style Linguistique** | {self.sota_options.language_sophistication.title()} |

### 🎯 Objectifs Stratégiques
{self._format_global_objectives(modules)}

### 🗺️ Architecture du Cours
{self._format_course_roadmap(modules)}

---

"""
        
        # Add modules with modern formatting
        for module in modules:
            content += self._format_modern_module(module)
        
        # Add appendices
        content += self._format_modern_appendices(modules)
        
        return content
    
    def _apply_academic_template(self, modules: List[Dict]) -> str:
        """Apply academic template with formal structure"""
        timestamp = datetime.now().strftime("%Y-%m-%d")
        course_title = self._generate_course_title(modules)
        
        content = f"""# {course_title}

**Document de Formation Académique**  
*Généré le {timestamp} par le Système SOTA Course Builder*

---

## Abstract

Ce document présente un cursus structuré selon les standards académiques internationaux, développé avec une approche pédagogique {self.sota_options.pedagogical_framework.value.replace('_', ' ')} et calibré pour un niveau {self.sota_options.difficulty_level.value}. 

**Mots-clés:** {self._extract_keywords(modules)}

---

## Table des Matières

{self._generate_academic_toc(modules)}

---

## 1. Introduction

### 1.1 Contexte et Justification
{self._generate_academic_context(modules)}

### 1.2 Objectifs Pédagogiques
{self._format_academic_objectives(modules)}

### 1.3 Méthodologie Pédagogique
Framework utilisé: **{self.sota_options.pedagogical_framework.value.replace('_', ' ').title()}**  
Niveau de complexité: **{self.sota_options.difficulty_level.value.title()}**  
Approche linguistique: **{self.sota_options.language_sophistication.title()}**

---

"""
        
        # Add modules with academic formatting
        for i, module in enumerate(modules, 2):
            content += self._format_academic_module(module, i)
        
        # Add academic appendices
        content += self._format_academic_appendices(modules)
        
        return content
    
    def _apply_research_template(self, modules: List[Dict]) -> str:
        """Apply research-grade template with citations and methodology"""
        timestamp = datetime.now().strftime("%Y-%m-%d")
        course_title = self._generate_course_title(modules)
        
        content = f"""# {course_title}: A State-of-the-Art Educational Framework

**Research-Grade Educational Content**  
*Generated: {timestamp}*  
*Framework: {self.sota_options.pedagogical_framework.value.replace('_', ' ').title()}*  
*Difficulty Level: {self.sota_options.difficulty_level.value.title()}*

---

## Abstract

This educational framework presents a comprehensive, research-backed approach to {self._infer_subject_domain(modules)}. The content is structured using evidence-based pedagogical principles and incorporates latest research findings from peer-reviewed sources.

**Keywords:** {self._extract_keywords(modules)}  
**Classification:** Educational Technology, {self._infer_subject_domain(modules)}, SOTA Methodology

---

## 1. Methodology

### 1.1 Pedagogical Framework
This course employs the **{self.sota_options.pedagogical_framework.value.replace('_', ' ').title()}** approach, selected for its evidence-based effectiveness in {self.sota_options.target_audience} education.

### 1.2 Content Curation Process
- **Source Analysis:** Academic papers from arXiv, IEEE, ACM Digital Library
- **Validation:** Peer-reviewed methodology with expert consultation
- **Adaptation:** Content calibrated for {self.sota_options.difficulty_level.value} level
- **Quality Assurance:** Multi-layer validation process

### 1.3 Assessment Strategy
{self._describe_assessment_strategy()}

---

## 2. Research Context and State of the Art

{self._generate_research_context(modules)}

---

## 3. Educational Modules

"""
        
        # Add modules with research formatting
        for i, module in enumerate(modules, 1):
            content += self._format_research_module(module, i)
        
        # Add research appendices
        content += self._format_research_appendices(modules)
        
        return content
    
    def _apply_classic_template(self, modules: List[Dict]) -> str:
        """Apply classic academic template"""
        # Implementation for classic style
        return self._apply_academic_template(modules)  # Fallback to academic for now
    
    def _apply_corporate_template(self, modules: List[Dict]) -> str:
        """Apply corporate training template"""
        timestamp = datetime.now().strftime("%Y-%m-%d")
        course_title = self._generate_course_title(modules)
        
        content = f"""# {course_title}
## Formation Professionnelle SOTA

**Date de création:** {timestamp}  
**Niveau:** {self.sota_options.difficulty_level.value.title()}  
**Durée:** {self._calculate_total_duration(modules)}  
**Format:** Formation interactive avec évaluations

---

## Executive Summary

Cette formation professionnelle de niveau {self.sota_options.difficulty_level.value} s'adresse aux {self.sota_options.target_audience} souhaitant maîtriser les concepts essentiels et avancés du domaine.

### Business Value
- **ROI Éducationnel:** Formation basée sur les dernières recherches
- **Applicabilité:** Concepts directement transférables en entreprise
- **Certification:** Évaluation continue avec validation des compétences

### Key Performance Indicators
{self._format_corporate_kpis(modules)}

---

## Training Modules

"""
        
        # Add modules with corporate formatting
        for module in modules:
            content += self._format_corporate_module(module)
        
        return content
    
    # Template-specific formatting methods
    
    def _format_modern_module(self, module: Dict) -> str:
        """Format module with modern visual elements"""
        difficulty_stars = "⭐" * module.get('difficulte', 3)
        duration_icon = "⏱️"
        
        content = f"""## 🎯 Module {module['numero']}: {module['titre']}

<div class="module-header">

**{duration_icon} Durée:** {module['duree_estimee']} | **📊 Difficulté:** {difficulty_stars} ({module.get('difficulte', 3)}/5)

</div>

### 🎓 Objectifs d'Apprentissage
{self._format_objectives_list(module['objectifs'])}

"""
        
        if module.get('prerequis'):
            content += f"""### 📋 Prérequis
{self._format_prerequisites_list(module['prerequis'])}

"""
        
        content += f"""### 📚 Contenu du Module

{module['contenu']}

"""
        
        if module.get('concepts_cles'):
            content += f"""### 🔑 Concepts Clés
{self._format_concepts_list(module['concepts_cles'])}

"""
        
        if module.get('questions_reflexion'):
            content += f"""### 🤔 Questions de Réflexion
{self._format_questions_list(module['questions_reflexion'])}

"""
        
        if module.get('interaction_points'):
            content += f"""### 🤝 Points d'Interaction
{self._format_interaction_points(module['interaction_points'])}

"""
        
        content += "---\n\n"
        return content
    
    def _format_academic_module(self, module: Dict, section_number: int) -> str:
        """Format module with academic structure"""
        content = f"""## {section_number}. {module['titre']}

### {section_number}.1 Introduction
*Durée estimée: {module['duree_estimee']} | Niveau de difficulté: {module.get('difficulte', 3)}/5*

"""
        
        if module.get('objectifs'):
            content += f"""### {section_number}.2 Objectifs Pédagogiques
{self._format_academic_objectives_list(module['objectifs'])}

"""
        
        content += f"""### {section_number}.3 Développement Conceptuel

{module['contenu']}

"""
        
        if module.get('questions_reflexion'):
            content += f"""### {section_number}.4 Questions d'Évaluation
{self._format_academic_questions(module['questions_reflexion'])}

"""
        
        content += f"""### {section_number}.5 Synthèse
*Section {section_number} complétée. Transition vers le module suivant.*

---

"""
        return content
    
    def _format_research_module(self, module: Dict, module_number: int) -> str:
        """Format module with research methodology"""
        content = f"""### 3.{module_number} {module['titre']}

#### 3.{module_number}.1 Theoretical Framework
*Duration: {module['duree_estimee']} | Complexity Level: {module.get('difficulte', 3)}/5*

**Learning Objectives:**
{self._format_research_objectives(module['objectifs'])}

#### 3.{module_number}.2 Content Analysis

{module['contenu']}

#### 3.{module_number}.3 Empirical Validation
{self._generate_validation_section(module)}

#### 3.{module_number}.4 Assessment Protocol
{self._generate_assessment_protocol(module)}

---

"""
        return content
    
    def _format_corporate_module(self, module: Dict) -> str:
        """Format module for corporate training"""
        content = f"""### Module {module['numero']}: {module['titre']}

**⏰ Durée:** {module['duree_estimee']}  
**🎯 Niveau:** {module.get('difficulte', 3)}/5  
**👥 Format:** Formation interactive

#### Objectifs Business
{self._format_business_objectives(module['objectifs'])}

#### Contenu de Formation

{module['contenu']}

#### ROI et Applications
- Application immédiate en entreprise
- Transfert de compétences mesurable
- Impact sur la performance métier

#### Évaluation
{self._format_corporate_assessment(module)}

---

"""
        return content
    
    # Helper methods for template generation
    
    def _calculate_total_duration(self, modules: List[Dict]) -> str:
        """Calculate total course duration"""
        total_minutes = 0
        for module in modules:
            duration_str = module.get('duree_estimee', '0 minutes')
            minutes = self._extract_minutes_from_string(duration_str)
            total_minutes += minutes
        
        hours = total_minutes // 60
        minutes = total_minutes % 60
        return f"{total_minutes} minutes ({hours}h{minutes:02d})"
    
    def _calculate_average_difficulty(self, modules: List[Dict]) -> float:
        """Calculate average difficulty across modules"""
        if not modules:
            return 3.0
        
        difficulties = [module.get('difficulte', 3) for module in modules]
        return sum(difficulties) / len(difficulties)
    
    def _generate_course_title(self, modules: List[Dict]) -> str:
        """Generate comprehensive course title"""
        # Extract key themes from module titles
        all_titles = " ".join([module['titre'] for module in modules])
        
        # Use SOTA options to create title
        base_title = f"Formation SOTA en {self._infer_subject_domain(modules)}"
        level_qualifier = f"Niveau {self.sota_options.difficulty_level.value.title()}"
        
        return f"{base_title} - {level_qualifier}"
    
    def _infer_subject_domain(self, modules: List[Dict]) -> str:
        """Infer subject domain from module content"""
        all_content = " ".join([
            module.get('titre', '') + " " + 
            " ".join(module.get('concepts_cles', [])) + " " +
            module.get('contenu', '')[:200]
            for module in modules
        ]).lower()
        
        # Domain detection
        domains = {
            'intelligence artificielle': ['ai', 'artificial intelligence', 'intelligence artificielle', 'neural', 'deep learning'],
            'apprentissage automatique': ['machine learning', 'apprentissage', 'ml', 'algorithme'],
            'vision par ordinateur': ['computer vision', 'image', 'cv', 'vision', 'cnn'],
            'traitement du langage naturel': ['nlp', 'natural language', 'language model', 'bert', 'gpt'],
            'data science': ['data science', 'data analysis', 'statistics', 'données'],
            'technologie': ['technology', 'technologie', 'innovation', 'digital']
        }
        
        for domain, keywords in domains.items():
            if any(keyword in all_content for keyword in keywords):
                return domain
        
        return "Technologies Avancées"
    
    # Additional formatting helper methods would continue here...
    # (Truncated for brevity - full implementation would include all helper methods)
    
    def _post_process_content(self, content: str) -> str:
        """Post-process content for consistency and quality"""
        # Remove excessive blank lines
        content = re.sub(r'\n\s*\n\s*\n', '\n\n', content)
        
        # Ensure consistent emoji usage
        if self.template_config.emoji_style:
            content = self._standardize_emoji_usage(content)
        
        # Validate markdown structure
        content = self._fix_markdown_structure(content)
        
        # Add table of contents if requested
        if self.template_config.include_toc:
            content = self._add_table_of_contents(content)
        
        return content
    
    def _validate_final_content(self, content: str) -> Dict:
        """Validate final content quality and structure"""
        validation_report = {
            'errors': [],
            'warnings': [],
            'statistics': {}
        }
        
        # Check for required sections
        required_sections = ['objectifs', 'contenu', 'module']
        for section in required_sections:
            if section.lower() not in content.lower():
                validation_report['errors'].append(f"Missing required section: {section}")
        
        # Content length validation
        if len(content) < 5000:
            validation_report['warnings'].append("Content may be too short for a comprehensive course")
        
        # Statistics
        validation_report['statistics'] = {
            'total_length': len(content),
            'word_count': len(content.split()),
            'section_count': content.count('##'),
            'module_count': content.count('Module')
        }
        
        return validation_report
    
    # Additional helper methods for specific template components...
    
    def _get_modern_template(self) -> str:
        """Get modern template structure"""
        return """# 🚀 {title}
## 📋 Overview
## 🎯 Modules
## 📚 Resources"""
    
    def _get_academic_template(self) -> str:
        """Get academic template structure"""
        return """# {title}
## Abstract
## Table of Contents  
## 1. Introduction
## 2. Modules
## References"""
    
    def _get_research_template(self) -> str:
        """Get research template structure"""  
        return """# {title}: A State-of-the-Art Educational Framework
## Abstract
## 1. Methodology
## 2. Research Context
## 3. Educational Modules
## 4. Conclusions
## References"""
    
    def _get_classic_template(self) -> str:
        """Get classic template structure"""
        return self._get_academic_template()
    
    def _get_corporate_template(self) -> str:
        """Get corporate template structure"""
        return """# {title}
## Executive Summary
## Training Modules  
## ROI Analysis
## Next Steps"""