import com.sun.jna.*;

public class KafelTest {
    public interface Kafel extends Library {
        public int kafel_set_policy(String policy, int sync_all_threads);
    }

    static public void main(String argv[]) throws Exception {
        Kafel kafel = (Kafel) Native.loadLibrary("kafel", Kafel.class);

        System.out.println("Exec prior to setting policy: ");
        System.out.println(new java.util.Scanner(Runtime.getRuntime().exec("uname -a").getInputStream()).useDelimiter("\\A").next());
        int sync_all_threads = 1;
        int rc = kafel.kafel_set_policy("POLICY a { KILL { connect, clone, fork, execve } } USE a DEFAULT ALLOW", sync_all_threads);
        if (rc == 0) {
            System.out.println("Kafel policy loaded");
        } else {
            System.out.println("Could not set policy :/");
        }

        try {
            System.out.println("Attempting to exec, which should fail");
            System.out.println(new java.util.Scanner(Runtime.getRuntime().exec("uname -a").getInputStream()).useDelimiter("\\A").next());
            System.out.println("If you can read this, that totally didn't work.");
        } catch (Exception e) {
            System.out.println("Yay, couldn't shell out. That happened in another thread, so I'm still alive.");
        }
    }
}
