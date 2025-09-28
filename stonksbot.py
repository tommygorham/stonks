#!/usr/bin/env python3
# This is a discord bot that runs this python program in discord
# Usage: 
# 1. Set environment variables:
#    - GUILD_ID: Your Discord server (guild) ID
#    - TOKEN: Your Discord bot token
#
# 2. Run the bot:
#    python3 ./stonksbot.py 
#
# 3. In Discord, you can run:
#    /stonks - Full analysis with CSV files
#    /quickstonks - Quick picks without files
#    /ping - Check bot latency

import discord
from discord import app_commands
from discord.ext import commands
import subprocess
import asyncio
import os
import sys
import platform
from datetime import datetime

# Environment variable configuration
GUILD_ID = os.getenv("GUILD_ID")
TOKEN = os.getenv("TOKEN")

# Check for required environment variables
if not GUILD_ID or not TOKEN:
    os_type = platform.system()
    print("ERROR: Required environment variables not set!\n")
    print("You must set both GUILD_ID and TOKEN environment variables.\n")
    
    if os_type == "Darwin":  # macOS
        print("macOS Instructions:")
        print("-------------------")
        print("For current session only:")
        print("  export GUILD_ID='your_guild_id_here'")
        print("  export TOKEN='your_bot_token_here'")
        print("  python3 ./stonksbot.py\n")
        print("For permanent setup (add to ~/.zshrc or ~/.bash_profile):")
        print("  echo 'export GUILD_ID=\"your_guild_id_here\"' >> ~/.zshrc")
        print("  echo 'export TOKEN=\"your_bot_token_here\"' >> ~/.zshrc")
        print("  source ~/.zshrc")
    
    elif os_type == "Windows":
        print("Windows Instructions:")
        print("--------------------")
        print("PowerShell (temporary):")
        print("  $env:GUILD_ID='your_guild_id_here'")
        print("  $env:TOKEN='your_bot_token_here'")
        print("  python stonksbot.py\n")
        print("Command Prompt (temporary):")
        print("  set GUILD_ID=your_guild_id_here")
        print("  set TOKEN=your_bot_token_here")
        print("  python stonksbot.py\n")
        print("For permanent setup (System Environment Variables):")
        print("  1. Open System Properties -> Advanced -> Environment Variables")
        print("  2. Add new User variables for GUILD_ID and TOKEN")
        print("  3. Restart your terminal")
    
    elif os_type == "Linux":
        print("Linux Instructions:")
        print("------------------")
        print("For current session only:")
        print("  export GUILD_ID='your_guild_id_here'")
        print("  export TOKEN='your_bot_token_here'")
        print("  python3 ./stonksbot.py\n")
        print("For permanent setup (add to ~/.bashrc):")
        print("  echo 'export GUILD_ID=\"your_guild_id_here\"' >> ~/.bashrc")
        print("  echo 'export TOKEN=\"your_bot_token_here\"' >> ~/.bashrc")
        print("  source ~/.bashrc")
    
    else:
        print(f"Unknown OS: {os_type}")
        print("Set environment variables according to your system's method.")
    
    print("\nNote: Replace 'your_guild_id_here' and 'your_bot_token_here' with actual values")
    print("Find your Guild ID: Enable Developer Mode in Discord -> Right-click server -> Copy ID")
    print("Find your Bot Token: https://discord.com/developers/applications -> Your App -> Bot -> Token")
    
    sys.exit(1)

# Convert GUILD_ID to integer
try:
    GUILD_ID = int(GUILD_ID)
except ValueError:
    print(f"ERROR: GUILD_ID must be a number. Got: {GUILD_ID}")
    sys.exit(1)

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

# Load bot
@bot.event
async def on_ready():
    print(f'Bot user {bot.user} connected')
    # Syncing guild-specific commands for instant availability
    try:
        guild = discord.Object(id=GUILD_ID)
        synced = await bot.tree.sync(guild=guild)
        print(f'Synced {len(synced)} commands to guild {guild.id}')
    except Exception as e:
        print(f'Error syncing commands: {e}')

# Bot Commands
@bot.tree.command(name="ping", description="Latency check")
@app_commands.guilds(GUILD_ID)
async def ping(ctx: discord.Interaction):
    await ctx.response.send_message(f"Pong {bot.latency * 1000:.0f} ms")

@bot.tree.command(name="stonks", description="Run trading analysis and get top picks")
@app_commands.guilds(GUILD_ID)
async def stonks(ctx: discord.Interaction):
    # Defer response since this might take a while
    await ctx.response.defer()
    
    try:
        # Run the shell script
        process = await asyncio.create_subprocess_shell(
            './run.sh',
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            cwd=os.path.dirname(os.path.abspath(__file__))  # Ensure we're in the right directory
        )
        
        # Wait for the process to complete with a timeout
        try:
            stdout, stderr = await asyncio.wait_for(process.communicate(), timeout=30.0)
        except asyncio.TimeoutError:
            process.kill()
            await ctx.followup.send("Analysis timed out. Please try again later.")
            return
        
        # Decode output
        output = stdout.decode('utf-8') if stdout else ""
        error = stderr.decode('utf-8') if stderr else ""
        
        # Parse the output to extract the relevant sections
        sections = []
        current_section = []
        capture = False
        
        for line in output.split('\n'):
            # Look for section headers
            if '--- Zacks #1 Rank Additions' in line:
                if current_section:
                    sections.append('\n'.join(current_section))
                current_section = [line]
                capture = True
            elif '--- Recent' in line and 'Purchases' in line:
                if current_section:
                    sections.append('\n'.join(current_section))
                current_section = [line]
                capture = True
            elif capture and line.strip():
                # Remove ANSI escape codes for terminal colors/links
                clean_line = line
                if '\033[' in clean_line:
                    # Extract just the ticker symbol from ANSI formatted links
                    import re
                    match = re.search(r'\033\]8;;.*?\033\\(.*?)\033\]8;;\033\\', clean_line)
                    if match:
                        clean_line = match.group(1)
                current_section.append(clean_line)
            elif capture and not line.strip():
                capture = False
        
        # Add the last section
        if current_section:
            sections.append('\n'.join(current_section))
        
        # Create embed with results
        embed = discord.Embed(
            title="Trading Analysis Results",
            color=discord.Color.green(),
            timestamp=datetime.now()
        )
        
        # Add each section as a field
        for section in sections:
            lines = section.split('\n')
            if lines:
                title = lines[0].replace('---', '').strip()
                # Get tickers (limit to avoid embed limits)
                tickers = [l for l in lines[1:] if l.strip()][:10]
                if tickers:
                    # Format tickers with code blocks for better visibility
                    ticker_text = '\n'.join([f"`{t}`" for t in tickers])
                    embed.add_field(
                        name=title,
                        value=ticker_text if ticker_text else "No data",
                        inline=False
                    )
        
        # Check if we got any data
        if not embed.fields:
            embed.description = "No trading data found. The analysis may have encountered an issue."
            if error:
                embed.add_field(name="Error Details", value=f"```{error[:500]}```", inline=False)
        
        # Add footer
        embed.set_footer(text="Data from QuiverQuant & Zacks")
        
        # Send the embed
        await ctx.followup.send(embed=embed)
        
        # Optional: Send CSV files if they were generated successfully
        analysis_dir = f"data/{datetime.now().strftime('%m-%d-%Y')}"
        if os.path.exists(analysis_dir):
            files_to_send = []
            for filename in os.listdir(analysis_dir):
                if filename.endswith('.csv'):
                    filepath = os.path.join(analysis_dir, filename)
                    if os.path.getsize(filepath) < 8_000_000:  # Discord file size limit
                        files_to_send.append(discord.File(filepath))
            
            if files_to_send[:3]:  # Send up to 3 files
                await ctx.followup.send("**Analysis files:**", files=files_to_send[:3])
        
    except FileNotFoundError:
        await ctx.followup.send("Could not find `run.sh`. Make sure the bot is in the correct directory.")
    except Exception as e:
        await ctx.followup.send(f"An error occurred: {str(e)[:1000]}")
@bot.tree.command(name="quickstonks", description="Get quick trading picks without files")
@app_commands.guilds(GUILD_ID)
async def quickstonks(ctx: discord.Interaction):
    # Defer response
    await ctx.response.defer()
    
    try:
        # Run a simplified version - just get the console output
        commands_to_run = [
            "cd scripts && python zacks.py",
            "cd scripts && python scrape.py congress | python analyzer.py congress",
            "cd scripts && python scrape.py insider | python analyzer.py insider"
        ]
        
        embed = discord.Embed(
            title="Quick Trading Picks",
            color=discord.Color.blue(),
            timestamp=datetime.now()
        )
        
        for cmd in commands_to_run:
            process = await asyncio.create_subprocess_shell(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                cwd=os.path.dirname(os.path.abspath(__file__))
            )
            
            try:
                stdout, stderr = await asyncio.wait_for(process.communicate(), timeout=15.0)
            except asyncio.TimeoutError:
                print(f"Command timed out: {cmd}")
                continue
                
            output = stdout.decode('utf-8') if stdout else ""
            error = stderr.decode('utf-8') if stderr else ""
            
            # Debug output for troubleshooting
            if error:
                print(f"Error in command '{cmd}': {error}")
            
            # Parse output for the section header and tickers
            lines = output.strip().split('\n')
            for i, line in enumerate(lines):
                # Look for section headers - be more inclusive in matching
                if '---' in line and any(keyword in line for keyword in ['Zacks', 'Top 5', 'Congress', 'Insider']):
                    title = line.replace('---', '').strip()
                    # Get the next few lines as tickers
                    tickers = []
                    for j in range(i+1, min(i+6, len(lines))):
                        if lines[j].strip() and not lines[j].startswith('---'):
                            # Clean ANSI codes - fixed regex patterns
                            import re
                            ticker_line = lines[j]
                            
                            # First try to extract from OSC 8 hyperlinks (terminal clickable links)
                            if '\033]8;;' in ticker_line:
                                # Extract text between the OSC 8 markers
                                match = re.search(r'\033\]8;;[^\033]*\033\\([^\033]+)\033\]8;;\033\\', ticker_line)
                                if match:
                                    ticker = match.group(1).strip()
                                else:
                                    # Fallback: just remove all ANSI codes
                                    ticker = re.sub(r'\033\[[^m]*m|\033\][^\\]*\\', '', ticker_line).strip()
                            else:
                                # Remove any ANSI color codes
                                ticker = re.sub(r'\033\[[^m]*m', '', ticker_line).strip()
                            
                            if ticker:
                                # Create clickable link to Yahoo Finance
                                tickers.append(f"[{ticker}](https://finance.yahoo.com/quote/{ticker})")
                    
                    if tickers:
                        embed.add_field(
                            name=title,
                            value='\n'.join(tickers),
                            inline=False
                        )
        
        if not embed.fields:
            embed.description = "No trading data found. The scripts may have encountered an issue."
            embed.set_footer(text="Check that all required scripts are present and working")
        else:
            embed.set_footer(text="Quick analysis - run /stonks for full data with files")
            
        await ctx.followup.send(embed=embed)
        
    except Exception as e:
        await ctx.followup.send(f"Error during quick analysis: {str(e)[:500]}")

bot.run(TOKEN)
