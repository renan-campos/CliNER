package gov.nih.nlm.nls.metamap;
import java.io.InputStream;
import java.io.PrintStream;
import java.io.BufferedReader;
import java.io.FileReader;
import java.io.File;
import java.util.List;
import java.util.ArrayList;
import se.sics.prologbeans.PrologSession;


// class used to perform cui lookup with metamap api
public class cuiLookup {
  
   MetaMapApi api;

   // set options
   public cuiLookup(String serverHostName, int serverPort) {
      this.api = new MetaMapApiImpl();
      this.api.setHost(serverHostName);
      this.api.setPort(serverPort);
      this.api.setOptions("--show_cuis -z");      
   }

   // print results of lookup to stdout
   public void printCuis(String term) 
   throws Exception
   {

      // get result
      List<Result> resultList = this.api.processCitationsFromString(term);

      // iterate over results
      for (Result result: resultList) {

         if (result != null) {

            if (result.getUtteranceList().size() == 0) {
               return;
            }

	    List<AcronymsAbbrevs> aaList = result.getAcronymsAbbrevsList();
    
            for (Utterance utterance: result.getUtteranceList()) {
	       
               for (PCM pcm: utterance.getPCMList()) {
                  
                  System.out.println("------------");
 
	          System.out.println("phrase: " + pcm.getPhrase().getPhraseText());

                  if ( pcm.getMappingList().size() < 1 ) {
                     System.out.println("concept id: None");
                     System.out.println("------------");
		     return;
                  }

                  for (Mapping map: pcm.getMappingList()) {

                     for (Ev mapEv: map.getEvList()) {

                        System.out.println("concept id: " + mapEv.getConceptId());

                     }

                  }                  
                  System.out.println("------------");
	
	      }
	   }
	 }
      }
   }

   public static void main(String[] args) 
   throws Exception
   {
      String serverhost = MetaMapApi.DEFAULT_SERVER_HOST;
      int serverport = MetaMapApi.DEFAULT_SERVER_PORT;

      // read phrase from stdin to lookup    
      new cuiLookup(serverhost, serverport).printCuis(args[0]);

   }
}
