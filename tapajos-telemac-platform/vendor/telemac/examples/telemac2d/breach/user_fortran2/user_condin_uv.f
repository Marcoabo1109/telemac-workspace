!                   *************************
                    SUBROUTINE USER_CONDIN_UV
!                   *************************
!
!
!***********************************************************************
! TELEMAC2D   V8P4
!***********************************************************************
!
!brief    USER INITIALISES THE PHYSICAL PARAMETERS U, V
!
!history  J-M HERVOUET (LNHE)
!+        30/08/2007
!+        V6P0
!+
!
!~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
!~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
!
      USE BIEF
      USE DECLARATIONS_TELEMAC
      USE DECLARATIONS_TELEMAC2D
      USE TPXO
      USE OKADA
!
      USE DECLARATIONS_SPECIAL
      IMPLICIT NONE
!
!+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
!
      INTEGER I
!
!-----------------------------------------------------------------------
!     CONSTANT VELOCITY ALONG THE CHANNEL TO HAVE AN HOTSTART
!
      DO I=1,NPOIN
        IF(MESH%Y%R(I).LE.26.D0) THEN
          U%R(I)=0.85D0
          V%R(I)=0.D0
        ENDIF
      ENDDO
!
!-----------------------------------------------------------------------
!
      RETURN
      END
