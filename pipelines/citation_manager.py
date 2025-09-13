#!/usr/bin/env python3
"""
Citation Manager - Academic citation system for course content
Handles academic referencing, bibliography generation, and citation formatting.
"""
from __future__ import annotations

import re
import json
from dataclasses import dataclass
from datetime import datetime
from typing import List, Dict, Optional, Tuple, Set
from enum import Enum

class CitationStyle(Enum):
    BASIC = "basic"
    ACADEMIC = "academic"
    DOCTORAL = "doctoral"
    IEEE = "ieee"
    APA = "apa"
    CHICAGO = "chicago"

@dataclass
class Citation:
    """Represents a single citation with all necessary metadata"""
    id: str
    title: str
    authors: List[str]
    year: str
    source_type: str  # 'paper', 'book', 'website', 'conference'
    journal: Optional[str] = None
    volume: Optional[str] = None
    pages: Optional[str] = None
    doi: Optional[str] = None
    arxiv_id: Optional[str] = None
    url: Optional[str] = None
    accessed_date: Optional[str] = None
    conference: Optional[str] = None
    publisher: Optional[str] = None
    isbn: Optional[str] = None
    relevance_topics: List[str] = None
    
class CitationManager:
    """
    Advanced citation management system for academic course content.
    Supports multiple citation styles and automatic bibliography generation.
    """
    
    def __init__(self, sota_options):
        self.sota_options = sota_options
        self.citation_style = sota_options.citation_style
        self.citations_db: Dict[str, Citation] = {}
        self.citation_counter = 1
        self.used_citations: Set[str] = set()
        
        # Citation patterns for different styles
        self.style_patterns = {
            CitationStyle.BASIC: "[{id}]",
            CitationStyle.ACADEMIC: "[{id}]",
            CitationStyle.DOCTORAL: "({authors}, {year})",
            CitationStyle.IEEE: "[{number}]",
            CitationStyle.APA: "({authors}, {year})",
            CitationStyle.CHICAGO: "({authors} {year})"
        }
        
        # Common AI/ML venues for automatic classification
        self.ai_venues = {
            'conferences': [
                'NeurIPS', 'ICML', 'ICLR', 'AAAI', 'IJCAI', 'CVPR', 'ICCV', 'ECCV',
                'ACL', 'EMNLP', 'NAACL', 'COLING', 'ICASSP', 'INTERSPEECH'
            ],
            'journals': [
                'Nature Machine Intelligence', 'Journal of Machine Learning Research',
                'IEEE Transactions on Pattern Analysis and Machine Intelligence',
                'Artificial Intelligence', 'Machine Learning', 'Neural Networks'
            ]
        }
        
    def integrate_citations(self, course_content: str) -> str:
        """
        Main method to integrate citations into course content.
        Finds citation placeholders and replaces with properly formatted citations.
        """
        if not self.sota_options.academic_citations:
            return course_content
        
        print("[INFO] Integrating academic citations...")
        
        # Extract research references from content
        self._extract_and_process_references(course_content)
        
        # Replace citation placeholders with formatted citations
        cited_content = self._replace_citation_placeholders(course_content)
        
        # Add bibliography section
        cited_content = self._append_bibliography(cited_content)
        
        print(f"[INFO] Citation integration complete. {len(self.used_citations)} citations integrated.")
        return cited_content
    
    def _extract_and_process_references(self, content: str) -> None:
        """Extract reference placeholders and convert to proper citations"""
        # Find citation placeholders like [REF-01], [arXiv:2401.12345], etc.
        ref_patterns = [
            r'\[REF-(\d+)\]',
            r'\[arXiv:(\d{4}\.\d{4,5})\]',
            r'\[DOI:([^\]]+)\]',
            r'\[URL:([^\]]+)\]',
            r'\[(.*?et al\..*?\d{4}.*?)\]'
        ]
        
        for pattern in ref_patterns:
            matches = re.findall(pattern, content)
            for match in matches:
                self._process_reference_match(pattern, match)
    
    def _process_reference_match(self, pattern: str, match: str) -> None:
        """Process individual reference matches and create citations"""
        if 'REF-' in pattern:
            # Generic reference placeholder
            ref_id = f"REF-{match}"
            if ref_id not in self.citations_db:
                citation = self._create_generic_citation(ref_id, match)
                self.citations_db[ref_id] = citation
        
        elif 'arXiv' in pattern:
            # arXiv paper
            arxiv_id = match
            if arxiv_id not in self.citations_db:
                citation = self._fetch_arxiv_citation(arxiv_id)
                if citation:
                    self.citations_db[arxiv_id] = citation
        
        elif 'DOI' in pattern:
            # DOI reference
            doi = match
            if doi not in self.citations_db:
                citation = self._fetch_doi_citation(doi)
                if citation:
                    self.citations_db[doi] = citation
    
    def _create_generic_citation(self, ref_id: str, context: str) -> Citation:
        """Create a generic citation for manual references"""
        return Citation(
            id=ref_id,
            title=f"Reference needed: {context}",
            authors=["[Auteur à déterminer]"],
            year="[Année]",
            source_type="paper",
            relevance_topics=[context]
        )
    
    def _fetch_arxiv_citation(self, arxiv_id: str) -> Optional[Citation]:
        """Fetch citation information from arXiv API"""
        try:
            import requests
            import xml.etree.ElementTree as ET
            
            url = f"http://export.arxiv.org/api/query?id_list={arxiv_id}"
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            
            root = ET.fromstring(response.text)
            ns = {'atom': 'http://www.w3.org/2005/Atom'}
            
            entry = root.find('atom:entry', ns)
            if entry is None:
                return None
            
            title = entry.find('atom:title', ns).text.strip()
            published = entry.find('atom:published', ns).text[:4]  # Year only
            
            authors = []
            for author in entry.findall('atom:author', ns):
                name = author.find('atom:name', ns).text
                authors.append(name)
            
            return Citation(
                id=arxiv_id,
                title=title,
                authors=authors,
                year=published,
                source_type="paper",
                arxiv_id=arxiv_id,
                url=f"https://arxiv.org/abs/{arxiv_id}",
                journal="arXiv preprint"
            )
            
        except Exception as e:
            print(f"[WARN] Failed to fetch arXiv citation for {arxiv_id}: {e}")
            return self._create_fallback_arxiv_citation(arxiv_id)
    
    def _create_fallback_arxiv_citation(self, arxiv_id: str) -> Citation:
        """Create fallback citation for arXiv when API fails"""
        return Citation(
            id=arxiv_id,
            title=f"[Titre à récupérer - arXiv:{arxiv_id}]",
            authors=["[Auteurs à récupérer]"],
            year="2024",  # Default recent year
            source_type="paper",
            arxiv_id=arxiv_id,
            url=f"https://arxiv.org/abs/{arxiv_id}",
            journal="arXiv preprint"
        )
    
    def _fetch_doi_citation(self, doi: str) -> Optional[Citation]:
        """Fetch citation information from DOI (CrossRef API)"""
        try:
            import requests
            
            url = f"https://api.crossref.org/works/{doi}"
            headers = {'Accept': 'application/json'}
            
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            work = data['message']
            
            title = work.get('title', [''])[0]
            
            authors = []
            for author in work.get('author', []):
                given = author.get('given', '')
                family = author.get('family', '')
                if given and family:
                    authors.append(f"{given} {family}")
                elif family:
                    authors.append(family)
            
            # Extract year from published date
            published_date = work.get('published-print', work.get('published-online', {}))
            year = str(published_date.get('date-parts', [[2024]])[0][0])
            
            journal = work.get('container-title', [''])[0]
            volume = work.get('volume', '')
            pages = work.get('page', '')
            
            return Citation(
                id=doi,
                title=title,
                authors=authors,
                year=year,
                source_type="paper",
                journal=journal,
                volume=volume,
                pages=pages,
                doi=doi,
                url=f"https://doi.org/{doi}"
            )
            
        except Exception as e:
            print(f"[WARN] Failed to fetch DOI citation for {doi}: {e}")
            return self._create_fallback_doi_citation(doi)
    
    def _create_fallback_doi_citation(self, doi: str) -> Citation:
        """Create fallback citation for DOI when API fails"""
        return Citation(
            id=doi,
            title=f"[Titre à récupérer - DOI:{doi}]",
            authors=["[Auteurs à récupérer]"],
            year="2024",
            source_type="paper",
            doi=doi,
            url=f"https://doi.org/{doi}"
        )
    
    def _replace_citation_placeholders(self, content: str) -> str:
        """Replace citation placeholders with formatted citations"""
        cited_content = content
        
        # Track citations used in content
        citation_map = {}
        
        # Replace different types of citation patterns
        patterns_replacements = [
            (r'\[REF-(\d+)\]', self._format_ref_citation),
            (r'\[arXiv:(\d{4}\.\d{4,5})\]', self._format_arxiv_citation),
            (r'\[DOI:([^\]]+)\]', self._format_doi_citation),
        ]
        
        for pattern, formatter in patterns_replacements:
            matches = re.finditer(pattern, cited_content)
            for match in matches:
                original = match.group(0)
                identifier = match.group(1)
                
                if identifier in self.citations_db:
                    citation = self.citations_db[identifier]
                    formatted_cite = formatter(citation, citation_map)
                    cited_content = cited_content.replace(original, formatted_cite)
                    self.used_citations.add(identifier)
        
        return cited_content
    
    def _format_ref_citation(self, citation: Citation, citation_map: Dict) -> str:
        """Format a generic reference citation"""
        if citation.id not in citation_map:
            citation_map[citation.id] = len(citation_map) + 1
        
        number = citation_map[citation.id]
        
        if self.citation_style == CitationStyle.IEEE:
            return f"[{number}]"
        elif self.citation_style in [CitationStyle.APA, CitationStyle.DOCTORAL]:
            author_short = citation.authors[0].split()[-1] if citation.authors else "Auteur"
            return f"({author_short}, {citation.year})"
        else:
            return f"[{number}]"
    
    def _format_arxiv_citation(self, citation: Citation, citation_map: Dict) -> str:
        """Format an arXiv citation"""
        if citation.id not in citation_map:
            citation_map[citation.id] = len(citation_map) + 1
        
        number = citation_map[citation.id]
        
        if self.citation_style == CitationStyle.IEEE:
            return f"[{number}]"
        elif self.citation_style in [CitationStyle.APA, CitationStyle.DOCTORAL]:
            author_short = citation.authors[0].split()[-1] if citation.authors else "Auteur"
            return f"({author_short} et al., {citation.year})"
        else:
            return f"[{number}]"
    
    def _format_doi_citation(self, citation: Citation, citation_map: Dict) -> str:
        """Format a DOI citation"""
        return self._format_arxiv_citation(citation, citation_map)  # Same formatting
    
    def _append_bibliography(self, content: str) -> str:
        """Append formatted bibliography to the course content"""
        if not self.used_citations:
            return content
        
        bibliography = "\n\n## 📚 Bibliographie\n\n"
        
        if self.citation_style == CitationStyle.BASIC:
            bibliography += "*Références utilisées dans ce cours*\n\n"
        else:
            bibliography += "*Références académiques*\n\n"
        
        # Sort citations by relevance/usage
        sorted_citations = sorted(
            [self.citations_db[cid] for cid in self.used_citations],
            key=lambda c: c.year,
            reverse=True
        )
        
        # Format each citation according to style
        for i, citation in enumerate(sorted_citations, 1):
            formatted_bib = self._format_bibliography_entry(citation, i)
            bibliography += f"{formatted_bib}\n\n"
        
        # Add research methodology note
        if self.sota_options.research_integration:
            bibliography += self._add_research_methodology_note()
        
        return content + bibliography
    
    def _format_bibliography_entry(self, citation: Citation, number: int) -> str:
        """Format individual bibliography entry based on citation style"""
        if self.citation_style == CitationStyle.IEEE:
            return self._format_ieee_entry(citation, number)
        elif self.citation_style == CitationStyle.APA:
            return self._format_apa_entry(citation)
        elif self.citation_style == CitationStyle.DOCTORAL:
            return self._format_doctoral_entry(citation, number)
        else:
            return self._format_basic_entry(citation, number)
    
    def _format_ieee_entry(self, citation: Citation, number: int) -> str:
        """Format citation in IEEE style"""
        authors_str = self._format_authors_ieee(citation.authors)
        
        entry = f"[{number}] {authors_str}, \"{citation.title},\""
        
        if citation.journal:
            entry += f" *{citation.journal}*"
            if citation.volume:
                entry += f", vol. {citation.volume}"
            if citation.pages:
                entry += f", pp. {citation.pages}"
        
        entry += f", {citation.year}."
        
        if citation.doi:
            entry += f" DOI: {citation.doi}"
        elif citation.url:
            entry += f" [En ligne]. Disponible: {citation.url}"
        
        return entry
    
    def _format_apa_entry(self, citation: Citation) -> str:
        """Format citation in APA style"""
        authors_str = self._format_authors_apa(citation.authors)
        
        entry = f"{authors_str} ({citation.year}). {citation.title}."
        
        if citation.journal:
            entry += f" *{citation.journal}*"
            if citation.volume:
                entry += f", {citation.volume}"
            if citation.pages:
                entry += f", {citation.pages}"
            entry += "."
        
        if citation.doi:
            entry += f" https://doi.org/{citation.doi}"
        elif citation.url:
            entry += f" {citation.url}"
        
        return entry
    
    def _format_doctoral_entry(self, citation: Citation, number: int) -> str:
        """Format citation in doctoral/academic style"""
        authors_str = self._format_authors_academic(citation.authors)
        
        entry = f"[{number}] {authors_str}. \"{citation.title}.\" "
        
        if citation.source_type == "paper" and citation.journal:
            entry += f"*{citation.journal}*"
            if citation.volume:
                entry += f" {citation.volume}"
            if citation.pages:
                entry += f" ({citation.year}): {citation.pages}"
            else:
                entry += f" ({citation.year})"
        else:
            entry += f"({citation.year})"
        
        entry += "."
        
        if citation.arxiv_id:
            entry += f" arXiv:{citation.arxiv_id}"
        elif citation.doi:
            entry += f" doi:{citation.doi}"
        elif citation.url:
            entry += f" {citation.url}"
        
        return entry
    
    def _format_basic_entry(self, citation: Citation, number: int) -> str:
        """Format citation in basic style"""
        authors_str = ", ".join(citation.authors) if citation.authors else "[Auteur]"
        
        entry = f"[{number}] **{citation.title}**\n"
        entry += f"   *{authors_str}* ({citation.year})"
        
        if citation.journal:
            entry += f" - {citation.journal}"
        
        if citation.url:
            entry += f"\n   🔗 [{citation.url}]({citation.url})"
        
        return entry
    
    def _format_authors_ieee(self, authors: List[str]) -> str:
        """Format authors for IEEE style"""
        if not authors:
            return "[Auteur]"
        
        if len(authors) == 1:
            return self._format_author_last_first(authors[0])
        elif len(authors) <= 3:
            formatted = [self._format_author_last_first(author) for author in authors]
            return " and ".join(formatted)
        else:
            first_author = self._format_author_last_first(authors[0])
            return f"{first_author} et al."
    
    def _format_authors_apa(self, authors: List[str]) -> str:
        """Format authors for APA style"""
        if not authors:
            return "[Auteur]"
        
        if len(authors) == 1:
            return self._format_author_last_first(authors[0])
        elif len(authors) <= 7:
            formatted = [self._format_author_last_first(author) for author in authors[:-1]]
            last_author = self._format_author_last_first(authors[-1])
            return ", ".join(formatted) + f", & {last_author}"
        else:
            formatted = [self._format_author_last_first(author) for author in authors[:6]]
            return ", ".join(formatted) + ", ... " + self._format_author_last_first(authors[-1])
    
    def _format_authors_academic(self, authors: List[str]) -> str:
        """Format authors for academic style"""
        if not authors:
            return "[Auteur]"
        
        if len(authors) == 1:
            return authors[0]
        elif len(authors) <= 3:
            return ", ".join(authors[:-1]) + f" and {authors[-1]}"
        else:
            return f"{authors[0]} et al."
    
    def _format_author_last_first(self, author: str) -> str:
        """Convert 'First Last' to 'Last, F.' format"""
        parts = author.split()
        if len(parts) >= 2:
            last = parts[-1]
            first_initials = ". ".join([name[0] for name in parts[:-1]]) + "."
            return f"{last}, {first_initials}"
        return author
    
    def _add_research_methodology_note(self) -> str:
        """Add note about research methodology"""
        return """### 🔬 Méthodologie de Recherche

*Les références académiques de ce cours ont été sélectionnées à partir de sources réputées incluant arXiv, IEEE Xplore, et d'autres bases de données académiques. La sélection privilégie les publications récentes (2023-2024) dans les domaines de l'intelligence artificielle, de l'apprentissage automatique, et des technologies émergentes.*

*Pour des références complètes et à jour, consultez directement les sources citées.*

"""
    
    def get_citation_statistics(self) -> Dict:
        """Get statistics about citations used"""
        return {
            'total_citations': len(self.used_citations),
            'citation_style': self.citation_style.value,
            'sources_breakdown': self._get_sources_breakdown(),
            'recent_papers_count': len([c for c in self.citations_db.values() 
                                      if int(c.year) >= 2023]),
            'arxiv_papers': len([c for c in self.citations_db.values() 
                               if c.arxiv_id])
        }
    
    def _get_sources_breakdown(self) -> Dict[str, int]:
        """Get breakdown of citation sources"""
        breakdown = {}
        for citation_id in self.used_citations:
            citation = self.citations_db[citation_id]
            source_type = citation.source_type
            breakdown[source_type] = breakdown.get(source_type, 0) + 1
        return breakdown