!                       *****************
                        SUBROUTINE ANAVEN
!                       *****************
!
!
!***********************************************************************
!  TOMAWAC VERSION 1.0    07/06/95       M. BENOIT (LNH) 30 87 72 66
!***********************************************************************
!
!     FONCTION  : PERMET LA SPECIFICATION D'UN VENT ANALYTIQUE
!                 (EVENTUELLEMENT VARIABLE EN TEMPS)
!
!-----------------------------------------------------------------------
!                             ARGUMENTS
! .________________.____.______________________________________________.
! !      NOM       !MODE!                   ROLE                       !
! !________________!____!______________________________________________!
! !    UV,VV       !<-- ! COMPOSANTES DU CHAMP DE VENT INITIAL         !
! !    X,Y         ! -->! COORDONNEES DES POINTS DU MAILLAGE 2D        !
! !    NPOIN2      ! -->! NOMBRE DE POINTS 2D                          !
! !    AT          !<-- ! TEMPS DU CALCUL                              !
! !________________!____!______________________________________________!
! MODE : -->(DONNEE NON MODIFIEE), <--(RESULTAT), <-->(DONNEE MODIFIEE)
!
!-----------------------------------------------------------------------
!
!  APPELE PAR : CONDIW,SEMIMP
!
!  SOUS-PROGRAMME APPELE : NEANT
!
!***********************************************************************
!
      USE DECLARATIONS_SPECIAL
      USE DECLARATIONS_TOMAWAC, ONLY :  NPOIN2, AT, UV, VV
!
      IMPLICIT NONE
!
!.....VARIABLES LOCALES
!     """""""""""""""""
      INTEGER  IP
      DOUBLE PRECISION UCONST, VCONST, VITES, TIMECHG
!
      VITES=20.D0
      TIMECHG=20000.D0
!
      IF (AT.LT.TIMECHG) THEN
        UCONST=20.D0-VITES*AT/TIMECHG
        VCONST=5.D0
      ELSE
        UCONST=VITES*(AT-TIMECHG)*1.D-5
        VCONST=5.D0+VITES*(AT-TIMECHG)*1.D-5
      ENDIF
!
      DO IP=1,NPOIN2
        UV(IP)=UCONST
        VV(IP)=VCONST
      ENDDO
!
      RETURN
      END
