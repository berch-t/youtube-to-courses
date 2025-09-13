#!/usr/bin/env python3
"""
Quality Assessor - Multi-dimensional quality analysis and enhancement
Validates and improves course content for pedagogical effectiveness.
"""
from __future__ import annotations

import re
import json
from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple, Any
from enum import Enum
from datetime import datetime

class QualityDimension(Enum):
    TECHNICAL_ACCURACY = "technical_accuracy"
    PEDAGOGICAL_FLOW = "pedagogical_flow"
    READABILITY = "readability"
    COMPLETENESS = "completeness"
    CONSISTENCY = "consistency"
    ENGAGEMENT = "engagement"
    ACCESSIBILITY = "accessibility"

@dataclass
class QualityMetric:
    """Represents a quality measurement"""
    dimension: QualityDimension
    score: float  # 0.0 to 1.0
    details: str
    suggestions: List[str]
    critical_issues: List[str]

@dataclass 
class QualityReport:
    """Comprehensive quality assessment report"""
    overall_score: float
    dimension_scores: Dict[QualityDimension, float]
    metrics: List[QualityMetric]
    enhancement_suggestions: List[str]
    critical_fixes: List[str]
    timestamp: str

class QualityAssessor:
    """
    Advanced quality assessment system for educational content.
    Provides multi-dimensional analysis and enhancement suggestions.
    """
    
    def __init__(self, sota_options):
        self.sota_options = sota_options
        
        # Quality thresholds
        self.thresholds = {
            'minimum_acceptable': 0.6,
            'good_quality': 0.75,
            'excellent_quality': 0.9
        }
        
        # Readability parameters (French language)
        self.readability_config = {
            'avg_sentence_length': {'beginner': 15, 'intermediate': 20, 'advanced': 25, 'expert': 30},
            'complex_words_ratio': {'beginner': 0.1, 'intermediate': 0.15, 'advanced': 0.25, 'expert': 0.35},
            'technical_terms_density': {'beginner': 0.05, 'intermediate': 0.1, 'advanced': 0.2, 'expert': 0.3}
        }
        
        # Pedagogical flow patterns
        self.flow_patterns = {
            'blooms_taxonomy': ['remember', 'understand', 'apply', 'analyze', 'evaluate', 'create'],
            'standard': ['introduction', 'concepts', 'examples', 'practice', 'assessment'],
            'constructivist': ['activation', 'exploration', 'explanation', 'elaboration', 'evaluation']
        }
        
        # Technical vocabulary for accuracy checking
        self.tech_vocabulary = {
            'ai_ml': [
                'neural network', 'deep learning', 'machine learning', 'algorithm',
                'gradient descent', 'backpropagation', 'overfitting', 'underfitting',
                'cross-validation', 'regularization', 'feature engineering'
            ],
            'computer_vision': [
                'convolutional', 'pooling', 'feature map', 'object detection',
                'segmentation', 'classification', 'augmentation'
            ],
            'nlp': [
                'tokenization', 'embedding', 'attention mechanism', 'transformer',
                'bert', 'gpt', 'language model', 'preprocessing'
            ]
        }
    
    def enhance_quality(self, course_content: str) -> str:
        """
        Main method to assess and enhance course quality.
        Returns improved content with quality enhancements applied.
        """
        if not self.sota_options.quality_enhancement:
            return course_content
        
        print("[INFO] Starting comprehensive quality assessment...")
        
        # Perform quality analysis
        quality_report = self._assess_quality(course_content)
        
        # Apply enhancements based on assessment
        enhanced_content = self._apply_quality_enhancements(course_content, quality_report)
        
        # Validate improvements
        final_report = self._assess_quality(enhanced_content)
        
        print(f"[INFO] Quality enhancement complete. Score: {quality_report.overall_score:.2f} → {final_report.overall_score:.2f}")
        
        return enhanced_content
    
    def _assess_quality(self, content: str) -> QualityReport:
        """Comprehensive quality assessment across all dimensions"""
        metrics = []
        
        # Assess each quality dimension
        for dimension in QualityDimension:
            metric = self._assess_dimension(content, dimension)
            metrics.append(metric)
        
        # Calculate overall score
        dimension_scores = {metric.dimension: metric.score for metric in metrics}
        overall_score = sum(dimension_scores.values()) / len(dimension_scores)
        
        # Generate enhancement suggestions
        enhancement_suggestions = self._generate_enhancement_suggestions(metrics)
        critical_fixes = self._identify_critical_fixes(metrics)
        
        return QualityReport(
            overall_score=overall_score,
            dimension_scores=dimension_scores,
            metrics=metrics,
            enhancement_suggestions=enhancement_suggestions,
            critical_fixes=critical_fixes,
            timestamp=datetime.now().isoformat()
        )
    
    def _assess_dimension(self, content: str, dimension: QualityDimension) -> QualityMetric:
        """Assess a specific quality dimension"""
        assessor_methods = {
            QualityDimension.TECHNICAL_ACCURACY: self._assess_technical_accuracy,
            QualityDimension.PEDAGOGICAL_FLOW: self._assess_pedagogical_flow,
            QualityDimension.READABILITY: self._assess_readability,
            QualityDimension.COMPLETENESS: self._assess_completeness,
            QualityDimension.CONSISTENCY: self._assess_consistency,
            QualityDimension.ENGAGEMENT: self._assess_engagement,
            QualityDimension.ACCESSIBILITY: self._assess_accessibility
        }
        
        method = assessor_methods.get(dimension)
        if method:
            return method(content)
        else:
            return QualityMetric(
                dimension=dimension,
                score=0.5,
                details="Assessment method not implemented",
                suggestions=[],
                critical_issues=[]
            )
    
    def _assess_technical_accuracy(self, content: str) -> QualityMetric:
        """Assess technical accuracy of the content"""
        score = 0.8  # Base score
        details = []
        suggestions = []
        critical_issues = []
        
        # Check for technical term usage
        content_lower = content.lower()
        
        # Detect domain
        domain = self._detect_content_domain(content)
        relevant_vocab = self.tech_vocabulary.get(domain, [])
        
        # Check for proper technical terminology
        correct_terms = 0
        total_terms = len(relevant_vocab)
        
        for term in relevant_vocab:
            if term in content_lower:
                correct_terms += 1
        
        if total_terms > 0:
            terminology_score = correct_terms / total_terms
            score = (score + terminology_score) / 2
        
        # Check for common technical errors
        common_errors = [
            (r'neural network', r'neuronal network', "Utiliser 'réseau de neurones' plutôt que 'réseau neuronal'"),
            (r'machine learning', r'apprentissage machine', "Préférer 'apprentissage automatique'"),
            (r'deep learning', r'apprentissage profond', "Terme correct en français")
        ]
        
        for pattern, replacement, suggestion in common_errors:
            if re.search(pattern, content_lower):
                suggestions.append(suggestion)
        
        # Check for mathematical notation consistency
        math_patterns = [r'\$.*?\$', r'\\[.*?\\]']
        math_count = sum(len(re.findall(pattern, content)) for pattern in math_patterns)
        
        if math_count > 0:
            details.append(f"Formules mathématiques détectées: {math_count}")
            if self.sota_options.include_math_formulas:
                score += 0.1
        
        details.append(f"Terminologie technique: {correct_terms}/{total_terms} termes détectés")
        
        return QualityMetric(
            dimension=QualityDimension.TECHNICAL_ACCURACY,
            score=min(score, 1.0),
            details="; ".join(details),
            suggestions=suggestions,
            critical_issues=critical_issues
        )
    
    def _assess_pedagogical_flow(self, content: str) -> QualityMetric:
        """Assess pedagogical flow and structure"""
        score = 0.7  # Base score
        details = []
        suggestions = []
        critical_issues = []
        
        # Check for pedagogical structure
        framework = self.sota_options.pedagogical_framework.value
        expected_patterns = self.flow_patterns.get(framework, [])
        
        # Analyze content structure
        sections = re.findall(r'###?\s+(.+)', content)
        
        if len(sections) < 3:
            critical_issues.append("Structure insuffisante: moins de 3 sections détectées")
            score -= 0.3
        
        # Check for learning objectives presence
        objectives_pattern = r'objectif|objective|goal|but'
        if re.search(objectives_pattern, content.lower()):
            score += 0.1
            details.append("Objectifs pédagogiques présents")
        else:
            suggestions.append("Ajouter des objectifs d'apprentissage clairs")
        
        # Check for assessment elements
        assessment_pattern = r'question|exercice|évaluation|test|quiz'
        if re.search(assessment_pattern, content.lower()):
            score += 0.1
            details.append("Éléments d'évaluation présents")
        else:
            suggestions.append("Intégrer des éléments d'évaluation")
        
        # Check for examples and illustrations
        example_pattern = r'exemple|example|illustration|démonstration'
        example_count = len(re.findall(example_pattern, content.lower()))
        
        if example_count >= 3:
            score += 0.1
            details.append(f"Exemples et illustrations: {example_count}")
        else:
            suggestions.append("Ajouter plus d'exemples concrets")
        
        # Progressive difficulty check
        difficulty_indicators = ['basique', 'simple', 'avancé', 'complexe', 'expert']
        progression_score = self._check_difficulty_progression(content, difficulty_indicators)
        score = (score + progression_score) / 2
        
        details.append(f"Structure pédagogique: {len(sections)} sections")
        
        return QualityMetric(
            dimension=QualityDimension.PEDAGOGICAL_FLOW,
            score=min(score, 1.0),
            details="; ".join(details),
            suggestions=suggestions,
            critical_issues=critical_issues
        )
    
    def _assess_readability(self, content: str) -> QualityMetric:
        """Assess content readability for target audience"""
        score = 0.7  # Base score
        details = []
        suggestions = []
        critical_issues = []
        
        # Calculate basic readability metrics
        sentences = self._split_into_sentences(content)
        words = content.split()
        
        if not sentences or not words:
            return QualityMetric(
                dimension=QualityDimension.READABILITY,
                score=0.0,
                details="Contenu vide ou non analysable",
                suggestions=["Vérifier le contenu"],
                critical_issues=["Contenu manquant"]
            )
        
        avg_sentence_length = len(words) / len(sentences)
        
        # Check against target level
        target_level = self.sota_options.difficulty_level.value
        expected_length = self.readability_config['avg_sentence_length'].get(target_level, 20)
        
        if avg_sentence_length <= expected_length * 1.2:
            score += 0.1
        elif avg_sentence_length > expected_length * 1.5:
            suggestions.append(f"Phrases trop longues (moy: {avg_sentence_length:.1f}, cible: {expected_length})")
            score -= 0.1
        
        # Complex words analysis
        complex_words = self._count_complex_words(words)
        complex_ratio = complex_words / len(words) if words else 0
        
        expected_ratio = self.readability_config['complex_words_ratio'].get(target_level, 0.15)
        
        if complex_ratio <= expected_ratio * 1.2:
            score += 0.1
        elif complex_ratio > expected_ratio * 1.5:
            suggestions.append(f"Trop de mots complexes ({complex_ratio:.2%}, cible: {expected_ratio:.2%})")
            score -= 0.1
        
        # Technical terms density
        tech_terms = self._count_technical_terms(content)
        tech_density = tech_terms / len(words) if words else 0
        
        expected_tech_density = self.readability_config['technical_terms_density'].get(target_level, 0.1)
        
        if tech_density <= expected_tech_density * 1.2:
            score += 0.05
        elif tech_density > expected_tech_density * 1.5:
            suggestions.append(f"Densité terminologique élevée ({tech_density:.2%})")
        
        # Language sophistication check
        sophistication_score = self._assess_language_sophistication(content)
        score = (score + sophistication_score) / 2
        
        details.extend([
            f"Longueur moyenne des phrases: {avg_sentence_length:.1f}",
            f"Mots complexes: {complex_ratio:.2%}",
            f"Densité technique: {tech_density:.2%}"
        ])
        
        return QualityMetric(
            dimension=QualityDimension.READABILITY,
            score=min(score, 1.0),
            details="; ".join(details),
            suggestions=suggestions,
            critical_issues=critical_issues
        )
    
    def _assess_completeness(self, content: str) -> QualityMetric:
        """Assess content completeness"""
        score = 0.6  # Base score
        details = []
        suggestions = []
        critical_issues = []
        
        # Required sections check
        required_sections = {
            'introduction': r'introduction|présentation|overview',
            'objectives': r'objectif|objective|goal|but',
            'content': r'contenu|content|développement',
            'examples': r'exemple|example|illustration',
            'assessment': r'évaluation|assessment|question|exercice'
        }
        
        present_sections = 0
        for section_name, pattern in required_sections.items():
            if re.search(pattern, content.lower()):
                present_sections += 1
                details.append(f"✓ {section_name}")
            else:
                suggestions.append(f"Ajouter section: {section_name}")
        
        completeness_ratio = present_sections / len(required_sections)
        score = completeness_ratio
        
        # Content depth analysis
        content_length = len(content)
        if content_length < 5000:
            suggestions.append("Contenu peut être trop court pour un cours complet")
            score -= 0.1
        elif content_length > 50000:
            suggestions.append("Contenu très long - vérifier la concision")
        
        # Module count check
        module_count = len(re.findall(r'module \d+|chapitre \d+', content.lower()))
        if module_count < 3:
            critical_issues.append(f"Nombre de modules insuffisant: {module_count}")
            score -= 0.2
        
        details.append(f"Sections présentes: {present_sections}/{len(required_sections)}")
        details.append(f"Longueur: {content_length} caractères")
        details.append(f"Modules: {module_count}")
        
        return QualityMetric(
            dimension=QualityDimension.COMPLETENESS,
            score=min(score, 1.0),
            details="; ".join(details),
            suggestions=suggestions,
            critical_issues=critical_issues
        )
    
    def _assess_consistency(self, content: str) -> QualityMetric:
        """Assess content consistency"""
        score = 0.8  # Base score
        details = []
        suggestions = []
        critical_issues = []
        
        # Terminology consistency
        terms_used = self._extract_key_terms(content)
        inconsistencies = self._find_terminology_inconsistencies(terms_used)
        
        if inconsistencies:
            score -= 0.1 * len(inconsistencies)
            for inconsistency in inconsistencies:
                suggestions.append(f"Standardiser: {inconsistency}")
        
        # Formatting consistency
        formatting_issues = self._check_formatting_consistency(content)
        if formatting_issues:
            score -= 0.05 * len(formatting_issues)
            suggestions.extend(formatting_issues)
        
        # Style consistency
        style_score = self._assess_style_consistency(content)
        score = (score + style_score) / 2
        
        details.append(f"Termes clés identifiés: {len(terms_used)}")
        details.append(f"Incohérences: {len(inconsistencies)}")
        
        return QualityMetric(
            dimension=QualityDimension.CONSISTENCY,
            score=min(score, 1.0),
            details="; ".join(details),
            suggestions=suggestions,
            critical_issues=critical_issues
        )
    
    def _assess_engagement(self, content: str) -> QualityMetric:
        """Assess content engagement level"""
        score = 0.7  # Base score
        details = []
        suggestions = []
        critical_issues = []
        
        # Interactive elements
        interactive_patterns = [
            r'question|pourquoi|comment',
            r'exercice|pratiquez|essayez',
            r'réfléchissez|pensez|analysez',
            r'🤔|🤝|💡|🔍'  # Emoji indicators
        ]
        
        interactive_count = 0
        for pattern in interactive_patterns:
            matches = len(re.findall(pattern, content.lower()))
            interactive_count += matches
        
        if interactive_count >= 10:
            score += 0.2
            details.append(f"Éléments interactifs: {interactive_count}")
        elif interactive_count < 5:
            suggestions.append("Ajouter plus d'éléments interactifs")
        
        # Engagement vocabulary
        engaging_words = [
            'découvrez', 'explorez', 'imaginez', 'visualisez',
            'remarquez', 'observez', 'comparez', 'analysez'
        ]
        
        engagement_score = 0
        for word in engaging_words:
            if word in content.lower():
                engagement_score += 1
        
        if engagement_score >= 5:
            score += 0.1
        
        # Questions and prompts
        question_count = len(re.findall(r'\?', content))
        if question_count >= 5:
            score += 0.1
            details.append(f"Questions: {question_count}")
        else:
            suggestions.append("Ajouter plus de questions pour engager le lecteur")
        
        details.append(f"Score d'engagement: {engagement_score}/10")
        
        return QualityMetric(
            dimension=QualityDimension.ENGAGEMENT,
            score=min(score, 1.0),
            details="; ".join(details),
            suggestions=suggestions,
            critical_issues=critical_issues
        )
    
    def _assess_accessibility(self, content: str) -> QualityMetric:
        """Assess content accessibility"""
        score = 0.8  # Base score
        details = []
        suggestions = []
        critical_issues = []
        
        # Alt text for visual elements
        image_patterns = [r'!\[([^\]]*)\]', r'<img[^>]+alt=["\']([^"\']*)["\']']
        images_with_alt = 0
        total_images = 0
        
        for pattern in image_patterns:
            matches = re.findall(pattern, content)
            total_images += len(matches)
            images_with_alt += len([m for m in matches if m.strip()])
        
        if total_images > 0:
            alt_ratio = images_with_alt / total_images
            score = (score + alt_ratio) / 2
            details.append(f"Images avec alt-text: {images_with_alt}/{total_images}")
            if alt_ratio < 0.8:
                suggestions.append("Ajouter des descriptions alternatives pour les images")
        
        # Structure headings
        headings = re.findall(r'^#+\s+(.+)', content, re.MULTILINE)
        if len(headings) >= 5:
            score += 0.1
            details.append(f"Structure: {len(headings)} titres")
        else:
            suggestions.append("Améliorer la structure avec plus de titres")
        
        # Language clarity
        clarity_score = self._assess_language_clarity(content)
        score = (score + clarity_score) / 2
        
        # Color-independent information
        color_dependencies = re.findall(r'rouge|vert|bleu|yellow|red|green|blue', content.lower())
        if color_dependencies:
            suggestions.append("Éviter la dépendance aux couleurs pour transmettre l'information")
            score -= 0.1
        
        return QualityMetric(
            dimension=QualityDimension.ACCESSIBILITY,
            score=min(score, 1.0),
            details="; ".join(details),
            suggestions=suggestions,
            critical_issues=critical_issues
        )
    
    # Helper methods for quality assessment
    
    def _detect_content_domain(self, content: str) -> str:
        """Detect the primary domain of the content"""
        content_lower = content.lower()
        
        domain_keywords = {
            'ai_ml': ['intelligence artificielle', 'machine learning', 'neural', 'deep learning'],
            'computer_vision': ['computer vision', 'image', 'vision', 'opencv'],
            'nlp': ['natural language', 'nlp', 'text processing', 'language model']
        }
        
        domain_scores = {}
        for domain, keywords in domain_keywords.items():
            score = sum(1 for keyword in keywords if keyword in content_lower)
            domain_scores[domain] = score
        
        return max(domain_scores, key=domain_scores.get) if domain_scores else 'general'
    
    def _split_into_sentences(self, content: str) -> List[str]:
        """Split content into sentences"""
        # Simple sentence splitting for French text
        sentences = re.split(r'[.!?]+\s+', content)
        return [s.strip() for s in sentences if s.strip()]
    
    def _count_complex_words(self, words: List[str]) -> int:
        """Count complex words (>3 syllables or >8 characters)"""
        complex_count = 0
        for word in words:
            clean_word = re.sub(r'[^\w]', '', word.lower())
            if len(clean_word) > 8 or self._count_syllables(clean_word) > 3:
                complex_count += 1
        return complex_count
    
    def _count_syllables(self, word: str) -> int:
        """Estimate syllable count for French words"""
        # Simple syllable counting heuristic
        word = word.lower()
        vowels = 'aeiouy'
        syllable_count = 0
        prev_was_vowel = False
        
        for char in word:
            is_vowel = char in vowels
            if is_vowel and not prev_was_vowel:
                syllable_count += 1
            prev_was_vowel = is_vowel
        
        return max(1, syllable_count)
    
    def _count_technical_terms(self, content: str) -> int:
        """Count technical terms in content"""
        content_lower = content.lower()
        tech_count = 0
        
        for domain_terms in self.tech_vocabulary.values():
            for term in domain_terms:
                tech_count += len(re.findall(r'\b' + re.escape(term) + r'\b', content_lower))
        
        return tech_count
    
    def _apply_quality_enhancements(self, content: str, quality_report: QualityReport) -> str:
        """Apply quality enhancements based on assessment"""
        enhanced_content = content
        
        # Apply critical fixes first
        for fix in quality_report.critical_fixes:
            enhanced_content = self._apply_critical_fix(enhanced_content, fix)
        
        # Apply enhancement suggestions
        for suggestion in quality_report.enhancement_suggestions:
            enhanced_content = self._apply_enhancement_suggestion(enhanced_content, suggestion)
        
        # Apply dimension-specific improvements
        for metric in quality_report.metrics:
            if metric.score < self.thresholds['minimum_acceptable']:
                enhanced_content = self._apply_dimension_improvement(enhanced_content, metric)
        
        return enhanced_content
    
    def _apply_critical_fix(self, content: str, fix: str) -> str:
        """Apply a critical fix to the content"""
        # Implementation would depend on the specific fix needed
        # For now, return content unchanged
        return content
    
    def _apply_enhancement_suggestion(self, content: str, suggestion: str) -> str:
        """Apply an enhancement suggestion"""
        # Implementation would depend on the specific suggestion
        # For now, return content unchanged
        return content
    
    def _apply_dimension_improvement(self, content: str, metric: QualityMetric) -> str:
        """Apply improvements for a specific quality dimension"""
        # Implementation would depend on the dimension and specific issues
        # For now, return content unchanged
        return content
    
    # Additional helper methods would be implemented here...
    
    def get_quality_summary(self, quality_report: QualityReport) -> str:
        """Generate a human-readable quality summary"""
        summary = f"""## 📊 Rapport de Qualité SOTA

**Score Global:** {quality_report.overall_score:.2f}/1.00 ({self._get_quality_label(quality_report.overall_score)})

### 📈 Scores par Dimension
"""
        
        for dimension, score in quality_report.dimension_scores.items():
            emoji = "🟢" if score >= 0.8 else "🟡" if score >= 0.6 else "🔴"
            dimension_name = dimension.value.replace('_', ' ').title()
            summary += f"- {emoji} **{dimension_name}:** {score:.2f}\n"
        
        if quality_report.enhancement_suggestions:
            summary += f"\n### 💡 Suggestions d'Amélioration\n"
            for suggestion in quality_report.enhancement_suggestions[:5]:
                summary += f"- {suggestion}\n"
        
        if quality_report.critical_fixes:
            summary += f"\n### ⚠️ Corrections Critiques\n"
            for fix in quality_report.critical_fixes:
                summary += f"- {fix}\n"
        
        summary += f"\n*Évaluation générée le {quality_report.timestamp}*"
        
        return summary
    
    def _get_quality_label(self, score: float) -> str:
        """Get quality label for a score"""
        if score >= self.thresholds['excellent_quality']:
            return "Excellent"
        elif score >= self.thresholds['good_quality']:
            return "Bien"
        elif score >= self.thresholds['minimum_acceptable']:
            return "Acceptable"
        else:
            return "À améliorer"