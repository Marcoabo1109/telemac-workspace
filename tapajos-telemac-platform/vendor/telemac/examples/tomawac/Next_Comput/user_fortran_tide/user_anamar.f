!                   **********************
                    SUBROUTINE USER_ANAMAR
!                   **********************
!***********************************************************************
! TOMAWAC
!***********************************************************************
!
!brief    USER SPECIFIES AN ANALYTICAL TIDE :
!+                WATER LEVEL AND CURRENT SPEED ARE VARIABLE IN TIME.
!
!~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
!| AT             |-->| COMPUTATION TIME
!| DEPTH          |<--| DEPTH OF WATER
!| DZHDT          |<--| VARIATION TEMPORELLE DE LA HAUTEUR DE MAREE
!| NPOIN2         |-->| NUMBER OF POINTS IN 2D
!| UC             |<--| CURRENT VELOCITY ALONG X AT THE MESH POINTS
!| VC             |<--| CURRENT VELOCITY ALONG Y AT THE MESH POINTS
!~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
!
      USE DECLARATIONS_SPECIAL
      USE INTERFACE_TOMAWAC, EX_USER_ANAMAR => USER_ANAMAR
      USE DECLARATIONS_TOMAWAC, ONLY : UC, VC, DEPTH, DZHDT, NPOIN2,  AT
      IMPLICIT NONE
      DOUBLE PRECISION UCONST,VCONST,HCONST
      INTEGER IP
!+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
!
!
!     COMMENT THE 5 LINES

!      WRITE(LU,*) 'CALL TO USER_ANAMAR'
!      WRITE(LU,*) 'IF YOU WANT AN ANALYTICAL TIDAL MODIFY ANAMAR'
!      WRITE(LU,*) 'OR MAY BE IT MEANS YOU DID NOT SPECIFY YOUR FILE'
!      WRITE(LU,*)'BINARY TIDAL WATER LEVEL FILE OR BINARY CURRENTS FILE'
!      CALL PLANTE(1)
!-----------------------------------------------------------------------
!     EXAMPLE 1
!-----------------------------------------------------------------------
!
      UCONST=5.D0
      VCONST=4.D0
      HCONST=0.5D0
!
      DO IP=1,NPOIN2
        UC(IP)   = UCONST*AT/350.D0
        VC(IP)   = VCONST*AT/350.D0
        DEPTH(IP)= HCONST*(350.D0+AT)/350.D0
        DZHDT(IP)= HCONST/350.D0
      ENDDO
!
!-----------------------------------------------------------------------
!
      RETURN
      END
