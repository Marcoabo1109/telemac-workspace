!                   ********************************
                    SUBROUTINE USER_PRERES_TELEMAC3D
!                   ********************************
     &(LEO)
!
!***********************************************************************
! TELEMAC3D
!***********************************************************************
!
!brief    USER PREPARES THE VARIABLES WHICH WILL BE WRITTEN TO
!+                THE RESULTS FILE OR TO THE LISTING.
!
!history  J-M HERVOUET (LNH)
!+        30/03/04
!+        V5P7
!+
!
!history  Y. AUDOUIN (LNHE)
!+        22/10/18
!+        V8P1
!+   Creation from PRERES_TELEMAC3D
!
!~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
!| LEO            |-->| IF TRUE WRITING IN OUTPUT FILE
!~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
!
      USE BIEF
      USE INTERFACE_TELEMAC3D, EX_USER_PRERES_TELEMAC3D =>
     &                            USER_PRERES_TELEMAC3D
      USE DECLARATIONS_TELEMAC3D
      USE DECLARATIONS_WAQTEL,ONLY : IND_O2
!
      IMPLICIT NONE
!
!+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
!
      LOGICAL, INTENT(IN) :: LEO
!
!+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
!
      INTEGER I,J
      DOUBLE PRECISION, PARAMETER :: EPS=1.D-10
!
!-----------------------------------------------------------------------
!
      IF(LEO) THEN
        DO I=1,NPOIN2
          J=(NPLAN-1)*NPOIN2+I
          PRIVE2D1%R(I)=CSO2%R(J)
          PRIVE2D2%R(I)=TA%ADR(IND_O2)%P%R(J)/MAX(CSO2%R(J),EPS)*100.D0
        ENDDO
      ENDIF
!
!-----------------------------------------------------------------------
!
      RETURN
      END
