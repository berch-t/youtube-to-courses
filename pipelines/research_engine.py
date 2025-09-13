#!/usr/bin/env python3
"""
Research Engine - Auto-integration with arXiv and academic sources
Enhances course content with latest research papers and citations.
"""
from __future__ import annotations

import re
import requests
import xml.etree.ElementTree as ET
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Tuple
from urllib.parse import quote_plus

@dataclass
class ResearchPaper:
    """Represents a research paper with metadata"""
    title: str
    authors: List[str]
    abstract: str
    arxiv_id: str
    published: str
    categories: List[str]
    url: str
    relevance_score: float = 0.0
    key_concepts: List[str] = None

class ResearchEngine:
    """
    Advanced research integration engine for academic content enhancement.
    Supports arXiv, Papers with Code, and other academic sources.
    """
    
    def __init__(self, sota_options):
        self.sota_options = sota_options
        self.arxiv_base_url = "http://export.arxiv.org/api/query"
        self.papers_with_code_api = "https://paperswithcode.com/api/v1"
        
        # Research configuration
        self.max_papers_per_topic = sota_options.max_references
        self.recent_papers_only = sota_options.recent_papers_only
        self.cutoff_date = datetime.now() - timedelta(days=730) if sota_options.recent_papers_only else None
        
        # AI/ML specific search terms and categories
        self.ai_categories = {
            'machine_learning': ['cs.LG', 'stat.ML'],
            'deep_learning': ['cs.LG', 'cs.CV', 'cs.CL'],
            'computer_vision': ['cs.CV'],
            'natural_language': ['cs.CL', 'cs.AI'],
            'reinforcement_learning': ['cs.LG', 'cs.AI'],
            'generative_ai': ['cs.LG', 'cs.CV', 'cs.CL'],
            'transformers': ['cs.LG', 'cs.CL'],
            'diffusion_models': ['cs.LG', 'cs.CV'],
            'llms': ['cs.CL', 'cs.AI'],
            'multimodal': ['cs.CV', 'cs.CL', 'cs.LG']
        }
        
        # Technical keywords for relevance scoring
        self.tech_keywords = [
            'neural network', 'deep learning', 'machine learning', 'transformer',
            'attention mechanism', 'diffusion', 'generative', 'llm', 'gpt',
            'bert', 'vision transformer', 'convolutional', 'recurrent',
            'reinforcement learning', 'unsupervised', 'supervised', 'self-supervised',
            'few-shot', 'zero-shot', 'fine-tuning', 'pre-training',
            'multimodal', 'computer vision', 'natural language processing'
        ]
    
    def enhance_with_research(self, transcript_data: Dict) -> Dict:
        """
        Main method to enhance transcript with research integration.
        Identifies topics and fetches relevant papers.
        """
        if not self.sota_options.research_integration:
            return transcript_data
        
        print("[INFO] Starting research integration...")
        
        # Extract topics and concepts from transcript
        topics = self._extract_research_topics(transcript_data)
        
        # Fetch papers for each topic
        all_papers = []
        for topic in topics:
            papers = self._search_arxiv_papers(topic)
            papers.extend(self._search_papers_with_code(topic))
            all_papers.extend(papers)
        
        # Rank and filter papers
        relevant_papers = self._rank_and_filter_papers(all_papers, topics)
        
        # Integrate papers into transcript structure
        enhanced_transcript = self._integrate_papers_into_content(
            transcript_data, 
            relevant_papers, 
            topics
        )
        
        print(f"[INFO] Research integration complete. Found {len(relevant_papers)} relevant papers.")
        return enhanced_transcript
    
    def _extract_research_topics(self, transcript_data: Dict) -> List[str]:
        """Extract research-worthy topics from transcript content"""
        full_content = " ".join([chunk['content'] for chunk in transcript_data['chunks']])
        
        # AI/ML topic detection
        detected_topics = []
        content_lower = full_content.lower()
        
        # Check for specific AI/ML topics
        topic_patterns = {
            'transformer': ['transformer', 'attention mechanism', 'bert', 'gpt'],
            'computer_vision': ['computer vision', 'image recognition', 'cnn', 'object detection'],
            'natural_language_processing': ['nlp', 'natural language', 'text processing', 'language model'],
            'deep_learning': ['deep learning', 'neural network', 'backpropagation'],
            'machine_learning': ['machine learning', 'ml algorithm', 'supervised learning'],
            'generative_ai': ['generative', 'gan', 'diffusion', 'stable diffusion', 'dalle'],
            'reinforcement_learning': ['reinforcement learning', 'q-learning', 'policy gradient'],
            'unsupervised_learning': ['unsupervised', 'clustering', 'dimensionality reduction'],
            'federated_learning': ['federated learning', 'distributed learning'],
            'explainable_ai': ['explainable', 'interpretable', 'xai', 'shap'],
            'multimodal': ['multimodal', 'vision-language', 'clip', 'blip'],
            'large_language_models': ['llm', 'large language model', 'chatgpt', 'claude']
        }
        
        for topic, keywords in topic_patterns.items():
            if any(keyword in content_lower for keyword in keywords):
                detected_topics.append(topic)
        
        # Extract specific technical terms
        tech_terms = []
        for keyword in self.tech_keywords:
            if keyword in content_lower:
                tech_terms.append(keyword)
        
        # Combine and deduplicate
        all_topics = list(set(detected_topics + tech_terms))
        
        return all_topics[:10]  # Limit to top 10 topics
    
    def _search_arxiv_papers(self, topic: str, max_results: int = 20) -> List[ResearchPaper]:
        """Search arXiv for papers related to the topic"""
        try:
            # Build search query
            search_terms = self._build_arxiv_search_query(topic)
            
            # Get relevant categories
            categories = self._get_categories_for_topic(topic)
            cat_filter = '+OR+'.join([f'cat:{cat}' for cat in categories])
            
            # Construct full query
            query = f"search_query=({search_terms})+AND+({cat_filter})"
            query += f"&start=0&max_results={max_results}"
            query += "&sortBy=submittedDate&sortOrder=descending"
            
            # Make API request
            response = requests.get(f"{self.arxiv_base_url}?{query}", timeout=10)
            response.raise_for_status()
            
            # Parse XML response
            papers = self._parse_arxiv_response(response.text, topic)
            
            # Filter by date if needed
            if self.recent_papers_only and self.cutoff_date:
                papers = [p for p in papers if self._parse_date(p.published) > self.cutoff_date]
            
            return papers
            
        except Exception as e:
            print(f"[WARN] arXiv search failed for topic '{topic}': {e}")
            return []
    
    def _build_arxiv_search_query(self, topic: str) -> str:
        """Build sophisticated arXiv search query"""
        # Clean and prepare topic
        topic_clean = topic.replace('_', ' ').lower()
        
        # Special handling for common AI topics
        query_mappings = {
            'transformer': 'transformer+OR+attention+mechanism+OR+bert+OR+gpt',
            'computer vision': 'computer+vision+OR+image+recognition+OR+cnn',
            'natural language processing': 'natural+language+processing+OR+nlp+OR+language+model',
            'large language models': 'large+language+model+OR+llm+OR+gpt+OR+bert',
            'generative ai': 'generative+model+OR+gan+OR+diffusion+OR+stable+diffusion',
            'deep learning': 'deep+learning+OR+neural+network+OR+deep+neural',
            'machine learning': 'machine+learning+OR+ml+OR+supervised+learning',
            'reinforcement learning': 'reinforcement+learning+OR+rl+OR+q+learning'
        }
        
        if topic_clean in query_mappings:
            return query_mappings[topic_clean]
        else:
            # Fallback: use topic as-is with synonyms
            terms = topic_clean.split()
            return '+'.join(terms)
    
    def _get_categories_for_topic(self, topic: str) -> List[str]:
        """Get relevant arXiv categories for a topic"""
        topic_clean = topic.replace('_', ' ').lower()
        
        # Map topics to arXiv categories
        for key, categories in self.ai_categories.items():
            if key.replace('_', ' ') in topic_clean or topic_clean in key.replace('_', ' '):
                return categories
        
        # Default categories for AI/ML
        return ['cs.LG', 'cs.AI', 'cs.CV', 'cs.CL']
    
    def _parse_arxiv_response(self, xml_content: str, topic: str) -> List[ResearchPaper]:
        """Parse arXiv API XML response"""
        try:
            root = ET.fromstring(xml_content)
            papers = []
            
            # Namespace handling
            ns = {'atom': 'http://www.w3.org/2005/Atom',
                  'arxiv': 'http://arxiv.org/schemas/atom'}
            
            for entry in root.findall('atom:entry', ns):
                # Extract basic info
                title = entry.find('atom:title', ns).text.strip()
                abstract = entry.find('atom:summary', ns).text.strip()
                published = entry.find('atom:published', ns).text
                arxiv_id = entry.find('atom:id', ns).text.split('/')[-1]
                
                # Extract authors
                authors = []
                for author in entry.findall('atom:author', ns):
                    name = author.find('atom:name', ns).text
                    authors.append(name)
                
                # Extract categories
                categories = []
                for category in entry.findall('atom:category', ns):
                    categories.append(category.get('term'))
                
                # Build URL
                url = f"https://arxiv.org/abs/{arxiv_id}"
                
                # Calculate relevance
                relevance = self._calculate_relevance(title, abstract, topic)
                
                paper = ResearchPaper(
                    title=title,
                    authors=authors,
                    abstract=abstract,
                    arxiv_id=arxiv_id,
                    published=published,
                    categories=categories,
                    url=url,
                    relevance_score=relevance
                )
                
                papers.append(paper)
            
            return papers
            
        except Exception as e:
            print(f"[WARN] Failed to parse arXiv response: {e}")
            return []
    
    def _search_papers_with_code(self, topic: str) -> List[ResearchPaper]:
        """Search Papers with Code for implementations"""
        if not self.sota_options.papers_with_code_integration:
            return []
        
        try:
            # Search for papers
            search_url = f"{self.papers_with_code_api}/papers/"
            params = {
                'q': topic.replace('_', ' '),
                'items_per_page': 10
            }
            
            response = requests.get(search_url, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            papers = []
            
            for item in data.get('results', []):
                paper = ResearchPaper(
                    title=item.get('title', ''),
                    authors=[],  # Papers with Code doesn't always have author info
                    abstract=item.get('abstract', ''),
                    arxiv_id=item.get('arxiv_id', ''),
                    published=item.get('published', ''),
                    categories=[],
                    url=item.get('url_abs', ''),
                    relevance_score=self._calculate_relevance(
                        item.get('title', ''), 
                        item.get('abstract', ''), 
                        topic
                    )
                )
                papers.append(paper)
            
            return papers
            
        except Exception as e:
            print(f"[WARN] Papers with Code search failed for topic '{topic}': {e}")
            return []
    
    def _calculate_relevance(self, title: str, abstract: str, topic: str) -> float:
        """Calculate relevance score for a paper"""
        text = f"{title} {abstract}".lower()
        topic_lower = topic.lower().replace('_', ' ')
        
        score = 0.0
        
        # Direct topic match
        if topic_lower in text:
            score += 3.0
        
        # Keyword matching
        topic_words = topic_lower.split()
        for word in topic_words:
            if word in text:
                score += 1.0
        
        # Technical keyword bonus
        for keyword in self.tech_keywords:
            if keyword.lower() in text:
                score += 0.5
        
        # Recent paper bonus
        try:
            pub_date = self._parse_date(abstract)  # This would need proper date extraction
            if pub_date and pub_date.year >= 2023:
                score += 1.0
        except:
            pass
        
        # Normalize score
        return min(score / 10.0, 1.0)
    
    def _rank_and_filter_papers(self, papers: List[ResearchPaper], topics: List[str]) -> List[ResearchPaper]:
        """Rank papers by relevance and filter top ones"""
        # Remove duplicates by arXiv ID
        unique_papers = {}
        for paper in papers:
            if paper.arxiv_id and paper.arxiv_id not in unique_papers:
                unique_papers[paper.arxiv_id] = paper
            elif not paper.arxiv_id and paper.title not in [p.title for p in unique_papers.values()]:
                unique_papers[paper.title] = paper
        
        # Sort by relevance score
        sorted_papers = sorted(unique_papers.values(), 
                             key=lambda p: p.relevance_score, 
                             reverse=True)
        
        # Filter top papers
        top_papers = sorted_papers[:self.max_papers_per_topic]
        
        return [p for p in top_papers if p.relevance_score > 0.3]  # Minimum relevance threshold
    
    def _integrate_papers_into_content(self, transcript_data: Dict, papers: List[ResearchPaper], topics: List[str]) -> Dict:
        """Integrate research papers into transcript content structure"""
        enhanced_transcript = transcript_data.copy()
        
        # Add research metadata
        enhanced_transcript['research_metadata'] = {
            'topics_identified': topics,
            'papers_found': len(papers),
            'integration_timestamp': datetime.now().isoformat(),
            'research_sources': ['arXiv', 'Papers with Code'] if self.sota_options.papers_with_code_integration else ['arXiv']
        }
        
        # Group papers by relevance to topics
        enhanced_transcript['research_papers'] = [
            {
                'title': paper.title,
                'authors': paper.authors,
                'abstract': paper.abstract[:500] + "..." if len(paper.abstract) > 500 else paper.abstract,
                'arxiv_id': paper.arxiv_id,
                'url': paper.url,
                'relevance_score': paper.relevance_score,
                'categories': paper.categories,
                'published': paper.published
            }
            for paper in papers
        ]
        
        # Add research context to chunks (for citation integration later)
        for chunk in enhanced_transcript['chunks']:
            chunk['suggested_references'] = self._find_relevant_papers_for_chunk(
                chunk['content'], papers
            )
        
        return enhanced_transcript
    
    def _find_relevant_papers_for_chunk(self, chunk_content: str, papers: List[ResearchPaper]) -> List[str]:
        """Find papers most relevant to a specific content chunk"""
        relevant_papers = []
        chunk_lower = chunk_content.lower()
        
        for paper in papers:
            # Check if paper concepts appear in this chunk
            title_words = paper.title.lower().split()
            matches = sum(1 for word in title_words if len(word) > 3 and word in chunk_lower)
            
            if matches >= 2:  # At least 2 significant word matches
                relevant_papers.append(paper.arxiv_id or paper.title[:50])
        
        return relevant_papers[:3]  # Max 3 references per chunk
    
    def _parse_date(self, date_string: str) -> Optional[datetime]:
        """Parse various date formats"""
        try:
            # Common arXiv format: 2024-01-15T10:30:00Z
            if 'T' in date_string:
                return datetime.fromisoformat(date_string.replace('Z', '+00:00'))
            # Simple date: 2024-01-15
            elif '-' in date_string:
                return datetime.strptime(date_string[:10], '%Y-%m-%d')
        except:
            pass
        return None
    
    def get_research_summary(self, papers: List[ResearchPaper]) -> str:
        """Generate a summary of research findings for inclusion in course"""
        if not papers:
            return ""
        
        summary = f"## 📚 Recherche Académique Récente\n\n"
        summary += f"*Basé sur l'analyse de {len(papers)} publications académiques récentes*\n\n"
        
        # Group papers by category/topic
        categories = {}
        for paper in papers:
            for cat in paper.categories[:2]:  # Top 2 categories
                if cat not in categories:
                    categories[cat] = []
                categories[cat].append(paper)
        
        for category, cat_papers in categories.items():
            summary += f"### {self._format_category_name(category)}\n"
            for paper in cat_papers[:3]:  # Top 3 papers per category
                summary += f"- **{paper.title}** ({paper.published[:4]})\n"
                summary += f"  *{paper.authors[0]} et al.* - [arXiv:{paper.arxiv_id}]({paper.url})\n"
                summary += f"  {paper.abstract[:200]}...\n\n"
        
        return summary
    
    def _format_category_name(self, category: str) -> str:
        """Format arXiv category names to readable text"""
        category_names = {
            'cs.LG': 'Apprentissage Automatique',
            'cs.AI': 'Intelligence Artificielle',
            'cs.CV': 'Vision par Ordinateur',
            'cs.CL': 'Traitement du Langage Naturel',
            'cs.NE': 'Réseaux de Neurones',
            'stat.ML': 'Apprentissage Statistique'
        }
        return category_names.get(category, category.replace('cs.', '').replace('stat.', '').upper())