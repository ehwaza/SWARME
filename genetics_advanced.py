"""
🧬 SWARNE V2.0 - Advanced Genetic Algorithms
Algorithmes génétiques avancés pour l'évolution de l'essaim
"""

import random
import numpy as np
from typing import List, Tuple, Dict, Optional
from enum import Enum
from dataclasses import dataclass
import logging

logger = logging.getLogger(__name__)


class SelectionMethod(Enum):
    """Méthodes de sélection"""
    ROULETTE = "roulette"           # Roulette wheel
    TOURNAMENT = "tournament"        # Tournoi
    RANK = "rank"                    # Basé sur le rang
    ELITISM = "elitism"              # Élitisme pur
    BOLTZMANN = "boltzmann"          # Sélection de Boltzmann


class CrossoverMethod(Enum):
    """Méthodes de crossover"""
    SINGLE_POINT = "single_point"    # Un point
    TWO_POINT = "two_point"          # Deux points
    UNIFORM = "uniform"              # Uniforme
    ARITHMETIC = "arithmetic"        # Arithmétique
    BLEND = "blend"                  # BLX-alpha


class MutationMethod(Enum):
    """Méthodes de mutation"""
    GAUSSIAN = "gaussian"            # Gaussienne
    UNIFORM = "uniform"              # Uniforme
    ADAPTIVE = "adaptive"            # Adaptative
    POLYNOMIAL = "polynomial"        # Polynomiale


@dataclass
class GeneticConfig:
    """Configuration des algorithmes génétiques"""
    selection_method: SelectionMethod = SelectionMethod.TOURNAMENT
    crossover_method: CrossoverMethod = CrossoverMethod.BLEND
    mutation_method: MutationMethod = MutationMethod.ADAPTIVE
    
    tournament_size: int = 3
    elitism_rate: float = 0.1
    crossover_rate: float = 0.8
    mutation_rate: float = 0.1
    
    # Adaptive mutation
    initial_mutation_rate: float = 0.3
    final_mutation_rate: float = 0.05
    
    # Diversity
    diversity_threshold: float = 0.1
    immigration_rate: float = 0.05
    
    # Speciation
    enable_speciation: bool = False
    compatibility_threshold: float = 3.0


class GeneticOperators:
    """Opérateurs génétiques avancés"""
    
    def __init__(self, config: GeneticConfig):
        self.config = config
        self.generation = 0
        
    # ================================================================
    # SÉLECTION
    # ================================================================
    
    def select_parents(self, population: List, fitness_scores: List[float], 
                      num_parents: int) -> List:
        """Sélection des parents selon la méthode configurée"""
        
        if self.config.selection_method == SelectionMethod.TOURNAMENT:
            return self._tournament_selection(population, fitness_scores, num_parents)
        elif self.config.selection_method == SelectionMethod.ROULETTE:
            return self._roulette_selection(population, fitness_scores, num_parents)
        elif self.config.selection_method == SelectionMethod.RANK:
            return self._rank_selection(population, fitness_scores, num_parents)
        elif self.config.selection_method == SelectionMethod.ELITISM:
            return self._elitist_selection(population, fitness_scores, num_parents)
        else:
            return self._tournament_selection(population, fitness_scores, num_parents)
    
    def _tournament_selection(self, population: List, fitness_scores: List[float],
                             num_parents: int) -> List:
        """Sélection par tournoi"""
        selected = []
        
        for _ in range(num_parents):
            # Sélectionner aléatoirement tournament_size individus
            tournament_indices = random.sample(
                range(len(population)), 
                min(self.config.tournament_size, len(population))
            )
            
            # Trouver le meilleur du tournoi
            best_idx = max(tournament_indices, key=lambda i: fitness_scores[i])
            selected.append(population[best_idx])
        
        return selected
    
    def _roulette_selection(self, population: List, fitness_scores: List[float],
                           num_parents: int) -> List:
        """Sélection par roulette (fitness proportionnelle)"""
        # Normaliser les fitness (éviter les valeurs négatives)
        min_fitness = min(fitness_scores)
        adjusted_fitness = [f - min_fitness + 1e-6 for f in fitness_scores]
        total_fitness = sum(adjusted_fitness)
        
        probabilities = [f / total_fitness for f in adjusted_fitness]
        
        selected = np.random.choice(
            population,
            size=num_parents,
            replace=True,
            p=probabilities
        )
        
        return list(selected)
    
    def _rank_selection(self, population: List, fitness_scores: List[float],
                       num_parents: int) -> List:
        """Sélection basée sur le rang"""
        # Trier par fitness
        sorted_indices = np.argsort(fitness_scores)
        
        # Probabilités basées sur le rang
        ranks = np.arange(1, len(population) + 1)
        probabilities = ranks / ranks.sum()
        
        selected_indices = np.random.choice(
            sorted_indices,
            size=num_parents,
            replace=True,
            p=probabilities
        )
        
        return [population[i] for i in selected_indices]
    
    def _elitist_selection(self, population: List, fitness_scores: List[float],
                          num_parents: int) -> List:
        """Sélection élitiste (meilleurs uniquement)"""
        sorted_indices = np.argsort(fitness_scores)[::-1]
        return [population[i] for i in sorted_indices[:num_parents]]
    
    # ================================================================
    # CROSSOVER
    # ================================================================
    
    def crossover(self, parent1, parent2):
        """Crossover selon la méthode configurée"""
        
        if random.random() > self.config.crossover_rate:
            return parent1, parent2  # Pas de crossover
        
        if self.config.crossover_method == CrossoverMethod.SINGLE_POINT:
            return self._single_point_crossover(parent1, parent2)
        elif self.config.crossover_method == CrossoverMethod.TWO_POINT:
            return self._two_point_crossover(parent1, parent2)
        elif self.config.crossover_method == CrossoverMethod.UNIFORM:
            return self._uniform_crossover(parent1, parent2)
        elif self.config.crossover_method == CrossoverMethod.ARITHMETIC:
            return self._arithmetic_crossover(parent1, parent2)
        elif self.config.crossover_method == CrossoverMethod.BLEND:
            return self._blend_crossover(parent1, parent2)
        else:
            return self._blend_crossover(parent1, parent2)
    
    def _single_point_crossover(self, parent1, parent2):
        """Crossover à un point"""
        # Obtenir les gènes (paramètres de stratégie)
        genes1 = self._get_genes(parent1)
        genes2 = self._get_genes(parent2)
        
        # Point de crossover
        point = random.randint(1, len(genes1) - 1)
        
        # Créer les enfants
        child1_genes = genes1[:point] + genes2[point:]
        child2_genes = genes2[:point] + genes1[point:]
        
        child1 = self._create_from_genes(parent1, child1_genes)
        child2 = self._create_from_genes(parent2, child2_genes)
        
        return child1, child2
    
    def _two_point_crossover(self, parent1, parent2):
        """Crossover à deux points"""
        genes1 = self._get_genes(parent1)
        genes2 = self._get_genes(parent2)
        
        # Deux points de crossover
        points = sorted(random.sample(range(1, len(genes1)), 2))
        p1, p2 = points
        
        # Créer les enfants
        child1_genes = genes1[:p1] + genes2[p1:p2] + genes1[p2:]
        child2_genes = genes2[:p1] + genes1[p1:p2] + genes2[p2:]
        
        child1 = self._create_from_genes(parent1, child1_genes)
        child2 = self._create_from_genes(parent2, child2_genes)
        
        return child1, child2
    
    def _uniform_crossover(self, parent1, parent2):
        """Crossover uniforme (chaque gène a 50% de chance)"""
        genes1 = self._get_genes(parent1)
        genes2 = self._get_genes(parent2)
        
        child1_genes = []
        child2_genes = []
        
        for g1, g2 in zip(genes1, genes2):
            if random.random() < 0.5:
                child1_genes.append(g1)
                child2_genes.append(g2)
            else:
                child1_genes.append(g2)
                child2_genes.append(g1)
        
        child1 = self._create_from_genes(parent1, child1_genes)
        child2 = self._create_from_genes(parent2, child2_genes)
        
        return child1, child2
    
    def _arithmetic_crossover(self, parent1, parent2, alpha: float = 0.5):
        """Crossover arithmétique"""
        genes1 = self._get_genes(parent1)
        genes2 = self._get_genes(parent2)
        
        # Moyenne pondérée
        child1_genes = [alpha * g1 + (1 - alpha) * g2 
                       for g1, g2 in zip(genes1, genes2)]
        child2_genes = [(1 - alpha) * g1 + alpha * g2 
                       for g1, g2 in zip(genes1, genes2)]
        
        child1 = self._create_from_genes(parent1, child1_genes)
        child2 = self._create_from_genes(parent2, child2_genes)
        
        return child1, child2
    
    def _blend_crossover(self, parent1, parent2, alpha: float = 0.5):
        """BLX-alpha crossover (Blend)"""
        genes1 = self._get_genes(parent1)
        genes2 = self._get_genes(parent2)
        
        child1_genes = []
        child2_genes = []
        
        for g1, g2 in zip(genes1, genes2):
            # Calculer l'intervalle étendu
            min_val = min(g1, g2)
            max_val = max(g1, g2)
            range_val = max_val - min_val
            
            # Étendre l'intervalle avec alpha
            lower = min_val - alpha * range_val
            upper = max_val + alpha * range_val
            
            # Générer valeurs aléatoires dans l'intervalle
            child1_genes.append(random.uniform(lower, upper))
            child2_genes.append(random.uniform(lower, upper))
        
        child1 = self._create_from_genes(parent1, child1_genes)
        child2 = self._create_from_genes(parent2, child2_genes)
        
        return child1, child2
    
    # ================================================================
    # MUTATION
    # ================================================================
    
    def mutate(self, individual):
        """Mutation selon la méthode configurée"""
        
        # Taux de mutation adaptatif
        mutation_rate = self._get_adaptive_mutation_rate()
        
        if random.random() > mutation_rate:
            return individual  # Pas de mutation
        
        if self.config.mutation_method == MutationMethod.GAUSSIAN:
            return self._gaussian_mutation(individual)
        elif self.config.mutation_method == MutationMethod.UNIFORM:
            return self._uniform_mutation(individual)
        elif self.config.mutation_method == MutationMethod.ADAPTIVE:
            return self._adaptive_mutation(individual)
        elif self.config.mutation_method == MutationMethod.POLYNOMIAL:
            return self._polynomial_mutation(individual)
        else:
            return self._gaussian_mutation(individual)
    
    def _get_adaptive_mutation_rate(self) -> float:
        """Taux de mutation adaptatif (décroît avec les générations)"""
        if self.generation == 0:
            return self.config.initial_mutation_rate
        
        # Décroissance linéaire
        progress = min(self.generation / 100.0, 1.0)
        rate = (self.config.initial_mutation_rate - 
                self.config.final_mutation_rate) * (1 - progress) + \
               self.config.final_mutation_rate
        
        return rate
    
    def _gaussian_mutation(self, individual):
        """Mutation gaussienne"""
        genes = self._get_genes(individual)
        mutated_genes = []
        
        for gene in genes:
            # Mutation avec distribution normale
            sigma = abs(gene) * 0.1  # 10% de la valeur
            mutated = gene + np.random.normal(0, sigma)
            mutated_genes.append(mutated)
        
        return self._create_from_genes(individual, mutated_genes)
    
    def _uniform_mutation(self, individual):
        """Mutation uniforme"""
        genes = self._get_genes(individual)
        mutated_genes = []
        
        for gene in genes:
            # Mutation uniforme dans [-10%, +10%]
            delta = gene * random.uniform(-0.1, 0.1)
            mutated = gene + delta
            mutated_genes.append(mutated)
        
        return self._create_from_genes(individual, mutated_genes)
    
    def _adaptive_mutation(self, individual):
        """Mutation adaptative (force dépend du fitness)"""
        # Si fitness élevé, mutation faible (fine-tuning)
        # Si fitness faible, mutation forte (exploration)
        fitness = getattr(individual, 'fitness_score', 0.5)
        
        genes = self._get_genes(individual)
        mutated_genes = []
        
        for gene in genes:
            # Force de mutation inversement proportionnelle au fitness
            strength = (1.0 - fitness) * 0.3
            mutated = gene + np.random.normal(0, abs(gene) * strength)
            mutated_genes.append(mutated)
        
        return self._create_from_genes(individual, mutated_genes)
    
    def _polynomial_mutation(self, individual, eta: float = 20.0):
        """Mutation polynomiale (plus sophistiquée)"""
        genes = self._get_genes(individual)
        mutated_genes = []
        
        for gene in genes:
            u = random.random()
            
            if u < 0.5:
                delta = (2 * u) ** (1 / (eta + 1)) - 1
            else:
                delta = 1 - (2 * (1 - u)) ** (1 / (eta + 1))
            
            mutated = gene + delta * abs(gene) * 0.1
            mutated_genes.append(mutated)
        
        return self._create_from_genes(individual, mutated_genes)
    
    # ================================================================
    # DIVERSITY & IMMIGRATION
    # ================================================================
    
    def check_diversity(self, population: List) -> float:
        """Calcule la diversité de la population"""
        if len(population) < 2:
            return 1.0
        
        # Calculer la variance moyenne des gènes
        all_genes = [self._get_genes(ind) for ind in population]
        genes_array = np.array(all_genes)
        
        # Variance normalisée
        variances = np.var(genes_array, axis=0)
        mean_variance = np.mean(variances)
        
        # Normaliser entre 0 et 1
        diversity = min(mean_variance / 100.0, 1.0)
        
        return diversity
    
    def introduce_immigrants(self, population: List, num_immigrants: int) -> List:
        """Introduit de nouveaux individus aléatoires"""
        immigrants = []
        
        if len(population) > 0:
            template = population[0]
            
            for _ in range(num_immigrants):
                # Créer un nouvel individu avec gènes aléatoires
                random_genes = [
                    random.uniform(g * 0.5, g * 1.5) 
                    for g in self._get_genes(template)
                ]
                immigrant = self._create_from_genes(template, random_genes)
                immigrants.append(immigrant)
        
        return immigrants
    
    # ================================================================
    # HELPERS
    # ================================================================
    
    def _get_genes(self, individual) -> List[float]:
        """Extrait les gènes (paramètres) d'un individu"""
        # Adapter selon la structure de votre Bee
        strategy = individual.strategy
        return [
            float(strategy.ema_fast),
            float(strategy.ema_slow),
            float(strategy.adx_threshold),
            float(strategy.rsi_overbought),
            float(strategy.rsi_oversold),
            float(strategy.atr_multiplier),
            float(strategy.risk_per_trade)
        ]
    
    def _create_from_genes(self, template, genes: List[float]):
        """Crée un nouvel individu à partir de gènes"""
        # Clone le template et applique les nouveaux gènes
        from copy import deepcopy
        new_individual = deepcopy(template)
        
        # Appliquer les gènes
        new_individual.strategy.ema_fast = int(max(5, min(50, genes[0])))
        new_individual.strategy.ema_slow = int(max(15, min(200, genes[1])))
        new_individual.strategy.adx_threshold = max(15, min(40, genes[2]))
        new_individual.strategy.rsi_overbought = max(60, min(90, genes[3]))
        new_individual.strategy.rsi_oversold = max(10, min(40, genes[4]))
        new_individual.strategy.atr_multiplier = max(0.5, min(3.0, genes[5]))
        new_individual.strategy.risk_per_trade = max(0.1, min(5.0, genes[6]))
        
        # Reset performance
        new_individual.trades = []
        new_individual.total_pnl = 0
        new_individual.fitness_score = 0
        
        return new_individual
    
    def increment_generation(self):
        """Incrémenter le compteur de génération"""
        self.generation += 1
        logger.info(f"🧬 Generation {self.generation} - "
                   f"Mutation rate: {self._get_adaptive_mutation_rate():.3f}")


# ================================================================
# EVOLUTION CONTROLLER
# ================================================================

class AdvancedEvolutionController:
    """Contrôleur d'évolution avancé"""
    
    def __init__(self, config: GeneticConfig):
        self.config = config
        self.operators = GeneticOperators(config)
        self.history = []
        
    def evolve(self, population: List, fitness_scores: List[float]) -> List:
        """Évolution complète d'une génération"""
        
        # 1. Vérifier la diversité
        diversity = self.operators.check_diversity(population)
        logger.info(f"📊 Population diversity: {diversity:.3f}")
        
        # 2. Immigration si diversité faible
        if diversity < self.config.diversity_threshold:
            num_immigrants = int(len(population) * self.config.immigration_rate)
            immigrants = self.operators.introduce_immigrants(population, num_immigrants)
            logger.info(f"🌍 Introducing {num_immigrants} immigrants")
        else:
            immigrants = []
        
        # 3. Élitisme - conserver les meilleurs
        num_elites = int(len(population) * self.config.elitism_rate)
        sorted_indices = np.argsort(fitness_scores)[::-1]
        elites = [population[i] for i in sorted_indices[:num_elites]]
        
        # 4. Sélection des parents
        num_parents = len(population) - num_elites - len(immigrants)
        parents = self.operators.select_parents(population, fitness_scores, num_parents)
        
        # 5. Reproduction (Crossover + Mutation)
        offspring = []
        for i in range(0, len(parents) - 1, 2):
            parent1, parent2 = parents[i], parents[i + 1]
            
            # Crossover
            child1, child2 = self.operators.crossover(parent1, parent2)
            
            # Mutation
            child1 = self.operators.mutate(child1)
            child2 = self.operators.mutate(child2)
            
            offspring.extend([child1, child2])
        
        # 6. Nouvelle population
        new_population = elites + offspring[:num_parents] + immigrants
        
        # 7. Incrémenter génération
        self.operators.increment_generation()
        
        # 8. Historique
        self.history.append({
            'generation': self.operators.generation,
            'diversity': diversity,
            'best_fitness': max(fitness_scores),
            'avg_fitness': np.mean(fitness_scores),
            'num_elites': num_elites,
            'num_immigrants': len(immigrants)
        })
        
        return new_population[:len(population)]
    
    def get_evolution_stats(self) -> Dict:
        """Statistiques d'évolution"""
        if not self.history:
            return {}
        
        return {
            'generations': len(self.history),
            'current_diversity': self.history[-1]['diversity'],
            'best_fitness_ever': max(h['best_fitness'] for h in self.history),
            'fitness_improvement': (
                self.history[-1]['best_fitness'] - self.history[0]['best_fitness']
                if len(self.history) > 1 else 0
            )
        }
