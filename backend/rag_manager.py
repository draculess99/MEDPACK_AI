import os
import chromadb
from typing import List, Dict

# Mock Documents
MOCK_DOCUMENTS = [
    {
        "id": "doc1",
        "text": "SOP-101 (IV Kits): In the event of an IV Kit shortage in the Emergency Department (ED), substitute with Pediatric IV Kits (if patient < 40kg) or use Central Line Kits for critical patients. Do not use expired IV Kits under any circumstances.",
        "metadata": {"type": "SOP", "item": "IV Kit", "department": "Emergency Department"}
    },
    {
        "id": "doc2",
        "text": "SOP-102 (IV Kits): ICU protocol for IV Kit shortage requires immediately halting elective surgeries and transferring all available IV Kits to the ICU. Contact Central Supply for emergency redistribution.",
        "metadata": {"type": "SOP", "item": "IV Kit", "department": "ICU"}
    },
    {
        "id": "doc3",
        "text": "SLA-001 (Medline): Medline guarantees emergency 4-hour delivery for Surgical Masks, N95 Respirators, and Isolation Gowns. A $500 premium applies to all emergency weekend orders.",
        "metadata": {"type": "SLA", "supplier": "Medline", "category": "PPE"}
    },
    {
        "id": "doc4",
        "text": "SOP-201 (Surgical Masks): Operating Room staff must use N95 respirators if standard Level 3 Surgical Masks are out of stock. Level 1 masks are not permitted in the OR.",
        "metadata": {"type": "SOP", "item": "Surgical Mask", "department": "Operating Room"}
    },
    {
        "id": "doc5",
        "text": "RECALL-2023-04 (Catheters): FDA Recall on Foley Catheters Lot #88392 due to balloon deflation issues. Immediately quarantine all stock. Substitute with straight catheters if continuous drainage is not strictly required.",
        "metadata": {"type": "Recall", "item": "Catheter"}
    },
    {
        "id": "doc6",
        "text": "EQUIP-001 (Oxygen Tubing): Standard 7ft oxygen tubing is universally compatible with Wall O2 flowmeters and portable tanks. For high-flow nasal cannula (HFNC), only use the specialized heated tubing (Item #HF-992).",
        "metadata": {"type": "Equipment Manual", "item": "Oxygen Tubing"}
    },
    {
        "id": "doc7",
        "text": "SOP-301 (Saline Flushes): If pre-filled 10mL saline flushes are unavailable, nurses may manually draw 10mL from a 1L normal saline bag using a sterile syringe. This requires an RN and takes approximately 2 extra minutes per flush.",
        "metadata": {"type": "SOP", "item": "Saline Flush"}
    },
    {
        "id": "doc8",
        "text": "SLA-002 (McKesson): Standard lead time for standard medical supplies (syringes, flushes, gauze) is 2 business days. Late deliveries incur a 5% credit back to the hospital account.",
        "metadata": {"type": "SLA", "supplier": "McKesson"}
    },
    {
        "id": "doc9",
        "text": "SOP-401 (Wound Care Packs): Labor and Delivery unit may substitute standard Wound Care Packs with basic gauze and surgical tape in non-hemorrhagic cases if standard packs fall below 5 units.",
        "metadata": {"type": "SOP", "item": "Wound Care Pack", "department": "Labor and Delivery"}
    },
    {
        "id": "doc10",
        "text": "RECALL-2024-01 (Monitoring Leads): Telemetry monitoring leads from Vendor X (Lot #441) have reports of false asystole alarms. Remove from ED and ICU immediately and use Vendor Y leads.",
        "metadata": {"type": "Recall", "item": "Monitoring Leads"}
    },
    {
        "id": "doc11",
        "text": "SOP-501 (General): Any supply drop below 20% of the 24-hour forecasted demand triggers a mandatory 'Command Center Escalation' to the Shift Supervisor. No exceptions.",
        "metadata": {"type": "SOP", "item": "General"}
    },
    {
        "id": "doc12",
        "text": "EQUIP-002 (Ventilator Circuits): Adult ventilator circuits cannot be safely adapted for pediatric use. If pediatric circuits are short in the NICU, immediately initiate a hospital-to-hospital transfer request.",
        "metadata": {"type": "Equipment Manual", "item": "Ventilator Circuit", "department": "NICU"}
    }
]

class RAGManager:
    _instance = None
    _collection = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(RAGManager, cls).__new__(cls)
            cls._instance._init_chroma()
        return cls._instance

    def _init_chroma(self):
        # Initialize ChromaDB client (in memory for simplicity/demo, or persistent)
        self.client = chromadb.Client()
        
        # Create or get collection
        try:
            self._collection = self.client.get_collection(name="medpack_knowledge")
        except:
            self._collection = self.client.create_collection(name="medpack_knowledge")
            
            # Load documents
            if self._collection.count() == 0:
                texts = [doc["text"] for doc in MOCK_DOCUMENTS]
                ids = [doc["id"] for doc in MOCK_DOCUMENTS]
                metadatas = [doc["metadata"] for doc in MOCK_DOCUMENTS]
                self._collection.add(
                    documents=texts,
                    metadatas=metadatas,
                    ids=ids
                )

    def query_rag(self, query_text: str, n_results: int = 2) -> str:
        """
        Query the RAG knowledge base and return a formatted string of the results.
        """
        if not self._collection:
            return "No RAG knowledge base available."

        try:
            results = self._collection.query(
                query_texts=[query_text],
                n_results=n_results
            )
            
            docs = results.get("documents", [[]])[0]
            if not docs:
                return "No relevant RAG documents found."
                
            formatted_docs = []
            for i, doc in enumerate(docs):
                formatted_docs.append(f"[RAG Document {i+1}]: {doc}")
            
            return "\n".join(formatted_docs)
        except Exception as e:
            return f"RAG Query Failed: {str(e)}"

# Global instance for easy import
rag_manager = RAGManager()
