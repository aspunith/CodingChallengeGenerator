import 'react'
import { SignIn, SignUp, SignedIn, SignedOut } from '@clerk/clerk-react'

export function AuthenticationPage() {
    return <div className = 'auth-container'>
        <SignedOut>
            <SignIn routing="path" path="/sign-in" />
            <SignUp routing="path" path="/sign-up" />
        </SignedOut>
        <SignedIn>
            <div className="redirect-message">
                <h2>Welcome back!</h2>
                <p>You are already signed in. You can now access the app.</p>
            </div>   
        </SignedIn>
    </div>
}