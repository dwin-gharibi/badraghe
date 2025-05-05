from typing import Dict, Optional, Set
import logging
from decorators.registry import get_seeder
from .base_seeder import BaseSeeder

class SeederManager:
    def __init__(self):
        self.seeded_tables: Set[str] = set()
        self.failed_tables: Set[str] = set()

    def seed_all(self, counts: Optional[Dict[str, int]] = None) -> Dict[str, int]:
        counts = counts or {}
        seeded = {}
        max_attempts = 10
        attempt_count = 0
        
        while len(self.seeded_tables) < len(get_seeder()) and attempt_count < max_attempts:
            attempt_count += 1
            progress_made = False
            
            for table_name, seeder_info in get_seeder().items():
                if table_name in self.seeded_tables or table_name in self.failed_tables:
                    continue
                    
                try:
                    result = self._seed_table_with_retry(table_name, counts.get(table_name, 10))
                    if result > 0:
                        seeded[table_name] = result
                        self.seeded_tables.add(table_name)
                        progress_made = True
                except Exception as e:
                    self.failed_tables.add(table_name)
            
            if not progress_made:
                remaining = set(get_seeder().keys()) - self.seeded_tables - self.failed_tables
                    
        return seeded

    def _seed_table_with_retry(self, table_name: str, count: int, max_retries: int = 2) -> int:
        retry_count = 0
        last_error = None
        
        while retry_count <= max_retries:
            try:
                return self.seed_table(table_name, count)
            except Exception as e:
                last_error = e
                retry_count += 1
        
        raise last_error if last_error else Exception(f"Failed to seed {table_name}")

    def seed_table(self, table_name: str, count: int = 10) -> int:
        seeder_info = get_seeder(table_name)
        if not seeder_info:
            raise ValueError(f"No seeder registered for table {table_name}")
            
        for dep in seeder_info['dependencies']:
            if dep not in self.seeded_tables:
                try:
                    self.seed_table(dep)
                except Exception as e:
                    raise Exception(f"Failed to seed dependency {dep} for {table_name}: {str(e)}")
                
        seeder = seeder_info['class']()
        try:
            result = seeder.seed(count)
            return result
        except Exception as e:
            pass
        finally:
            seeder.close()

    def reset_seeded_tables(self) -> None:
        self.seeded_tables = set()
        self.failed_tables = set()