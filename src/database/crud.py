from sqlalchemy.orm import Session
from typing import List, Dict, Any

from src.database.models import VotationMetadata

def save_votation_metadata(db: Session, votation_metadata: List[Dict[str, Any]]) -> int:
	"""
	Saves the law metadata to the db. Returns the number of new votations added.
	Args:
		db (Session): Database session.
		votation_metadata (List[Dict[str, Any]]): List of votation metadata dictionaries.
			Each dictionary should contain keys: id, date, title, type, result, downloaded, and analyzed.
	Returns:
		int: Number of new votations added to the database.
	"""
	if not votation_metadata:
		return 0
	
	incoming_ids = {data['id'] for data in votation_metadata}

	existing_ids_query = db.query(VotationMetadata.id).filter(VotationMetadata.id.in_(incoming_ids))
	existing_ids = {id_tuple[0] for id_tuple in existing_ids_query}
	
	new_data_to_add = [
        data for data in votation_metadata if data['id'] not in existing_ids
    ]

	if not new_data_to_add:
		return 0

	new_votations_objects = [VotationMetadata(**data) for data in new_data_to_add]

	db.add_all(new_votations_objects)
	db.commit()

	num_added = len(new_votations_objects)

	return num_added