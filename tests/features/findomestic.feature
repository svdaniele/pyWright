Feature: WEB - Findomestic Demo - Prestito personale Auto

  @TC04
  Scenario: WEB TC04 Findomestic demo Prestito personale Auto nuova importo personalizzato
  Given Accedi a findomestic.it
  When Naviga in 'Prestito Personali Auto'
  	And Richiedi prestito personale 'Auto Nuova' con importo 25000
  Then Verifica flusso E2E 'Richiesta Prestito Online'
  	And Risolvo verifiche
